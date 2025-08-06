"""
Newsletter Routes
Simple newsletter signup and management
"""

from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re
import uuid

from app import db, admin_required
from .models import NewsletterSubscriber, NewsletterCampaign, NewsletterSend, NewsletterTemplate

newsletter_bp = Blueprint('newsletter', __name__)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Newsletter signup endpoint"""
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        source = data.get('source', 'website')
        
        # Validate email
        if not email or not EMAIL_REGEX.match(email):
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        # Check if already subscribed
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            if existing.subscribed:
                return jsonify({'message': 'You are already subscribed to our newsletter'}), 200
            else:
                # Resubscribe
                existing.subscribed = True
                existing.unsubscribed_at = None
                existing.updated_at = datetime.now(timezone.utc)
                db.session.commit()
                return jsonify({'message': 'Welcome back! You have been resubscribed'}), 200
        
        # Create new subscriber
        subscriber = NewsletterSubscriber(
            email=email,
            name=name,
            source=source,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            confirmed=True  # Auto-confirm for simplicity
        )
        
        db.session.add(subscriber)
        db.session.commit()
        
        # TODO: Send welcome email (optional)
        
        return jsonify({
            'message': 'Thank you for subscribing! You will receive our newsletter updates.',
            'subscriber_id': subscriber.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to subscribe. Please try again.'}), 500

@newsletter_bp.route('/unsubscribe')
def unsubscribe():
    """Newsletter unsubscribe page"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if token:
        subscriber = NewsletterSubscriber.query.filter_by(subscription_token=token).first()
    elif email:
        subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
    else:
        return render_template('newsletter/unsubscribe.html', error="Invalid unsubscribe link")
    
    if not subscriber:
        return render_template('newsletter/unsubscribe.html', error="Subscriber not found")
    
    if request.method == 'POST' or request.args.get('confirm') == '1':
        subscriber.subscribed = False
        subscriber.unsubscribed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return render_template('newsletter/unsubscribe.html', success=True, email=subscriber.email)
    
    return render_template('newsletter/unsubscribe.html', subscriber=subscriber)

# Admin newsletter management
@newsletter_bp.route('/admin/subscribers')
@login_required
@admin_required
def admin_subscribers():
    """Newsletter subscribers management"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'subscribed')
    
    query = NewsletterSubscriber.query
    
    if status == 'subscribed':
        query = query.filter_by(subscribed=True)
    elif status == 'unsubscribed':
        query = query.filter_by(subscribed=False)
    
    subscribers = query.order_by(NewsletterSubscriber.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    stats = {
        'total': NewsletterSubscriber.query.count(),
        'subscribed': NewsletterSubscriber.query.filter_by(subscribed=True).count(),
        'unsubscribed': NewsletterSubscriber.query.filter_by(subscribed=False).count(),
        'confirmed': NewsletterSubscriber.query.filter_by(confirmed=True).count()
    }
    
    return render_template('newsletter/admin/subscribers.html', 
                         subscribers=subscribers, stats=stats, status=status)

@newsletter_bp.route('/api/admin/campaigns', methods=['GET'])
@login_required
@admin_required
def api_get_campaigns():
    """Get newsletter campaigns"""
    campaigns = NewsletterCampaign.query.order_by(NewsletterCampaign.created_at.desc()).all()
    
    return jsonify([{
        'id': campaign.id,
        'name': campaign.name,
        'subject': campaign.subject,
        'status': campaign.status,
        'recipients_count': campaign.recipients_count,
        'sent_count': campaign.sent_count,
        'opened_count': campaign.opened_count,
        'created_at': campaign.created_at.isoformat(),
        'send_at': campaign.send_at.isoformat() if campaign.send_at else None
    } for campaign in campaigns])

@newsletter_bp.route('/api/admin/campaigns', methods=['POST'])
@login_required
@admin_required
def api_create_campaign():
    """Create newsletter campaign from generated content"""
    data = request.get_json()
    
    # Get the generated content
    from blog.models import GeneratedContent
    content = GeneratedContent.query.get_or_404(data['generated_content_id'])
    
    if content.content_type != 'newsletter':
        return jsonify({'error': 'Content is not a newsletter'}), 400
    
    # Create campaign
    campaign = NewsletterCampaign(
        name=data.get('name', f"Newsletter - {content.title}"),
        subject=content.title,
        content_html=_convert_to_html_email(content.content),
        content_text=_convert_to_text_email(content.content),
        generated_content_id=content.id,
        send_at=datetime.fromisoformat(data['send_at']) if data.get('send_at') else None
    )
    
    # Count potential recipients
    active_subscribers = NewsletterSubscriber.query.filter_by(
        subscribed=True, confirmed=True
    ).count()
    campaign.recipients_count = active_subscribers
    
    db.session.add(campaign)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Newsletter campaign created',
        'campaign_id': campaign.id
    })

@newsletter_bp.route('/api/admin/campaigns/<int:campaign_id>/send', methods=['POST'])
@login_required
@admin_required
def api_send_campaign(campaign_id):
    """Send newsletter campaign"""
    campaign = NewsletterCampaign.query.get_or_404(campaign_id)
    
    if campaign.status not in ['draft', 'scheduled']:
        return jsonify({'error': 'Campaign cannot be sent in current status'}), 400
    
    try:
        # Get active subscribers
        subscribers = NewsletterSubscriber.query.filter_by(
            subscribed=True, confirmed=True
        ).all()
        
        campaign.status = 'sending'
        campaign.sent_at = datetime.now(timezone.utc)
        db.session.commit()
        
        sent_count = 0
        failed_count = 0
        
        # Send emails (simplified - in production use a queue)
        for subscriber in subscribers:
            try:
                # Create send record
                send_record = NewsletterSend(
                    campaign_id=campaign.id,
                    subscriber_id=subscriber.id,
                    email_address=subscriber.email
                )
                db.session.add(send_record)
                
                # Send email
                success = _send_email(
                    to_email=subscriber.email,
                    to_name=subscriber.name,
                    subject=campaign.subject,
                    html_content=campaign.content_html,
                    text_content=campaign.content_text,
                    unsubscribe_token=subscriber.subscription_token
                )
                
                if success:
                    send_record.status = 'sent'
                    send_record.sent_at = datetime.now(timezone.utc)
                    sent_count += 1
                else:
                    send_record.status = 'failed'
                    send_record.error_message = 'Failed to send'
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                continue
        
        # Update campaign
        campaign.status = 'sent'
        campaign.sent_count = sent_count
        campaign.completed_at = datetime.now(timezone.utc)
        subscriber.last_email_sent = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Campaign sent to {sent_count} subscribers',
            'sent_count': sent_count,
            'failed_count': failed_count
        })
        
    except Exception as e:
        campaign.status = 'failed'
        db.session.commit()
        return jsonify({'error': f'Failed to send campaign: {str(e)}'}), 500

def _convert_to_html_email(markdown_content):
    """Convert markdown newsletter to HTML email format"""
    import markdown
    html = markdown.markdown(markdown_content)
    
    # Wrap in basic email template
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Center Deep Newsletter</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
            .header {{ background: #1e3a8a; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            a {{ color: #1e3a8a; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Center Deep Newsletter</h1>
        </div>
        <div class="content">
            {html}
        </div>
        <div class="footer">
            <p>You received this email because you subscribed to Center Deep Newsletter.</p>
            <p><a href="{{{{ unsubscribe_url }}}}">Unsubscribe</a> | <a href="https://centerdeep.com">Visit our website</a></p>
        </div>
    </body>
    </html>
    """

def _convert_to_text_email(markdown_content):
    """Convert markdown newsletter to plain text"""
    # Simple markdown to text conversion
    import re
    text = markdown_content
    text = re.sub(r'#+ ', '', text)  # Remove headers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links
    
    return text + "\n\n---\nUnsubscribe: {{ unsubscribe_url }}\nCenter Deep: https://centerdeep.com"

def _send_email(to_email, to_name, subject, html_content, text_content, unsubscribe_token):
    """Send email using SMTP (simplified)"""
    try:
        # In a real implementation, you'd use a service like SendGrid, Mailgun, etc.
        # For now, we'll just log it and return True
        
        unsubscribe_url = url_for('newsletter.unsubscribe', token=unsubscribe_token, _external=True)
        
        # Replace template variables
        html_content = html_content.replace('{{ unsubscribe_url }}', unsubscribe_url)
        text_content = text_content.replace('{{ unsubscribe_url }}', unsubscribe_url)
        
        print(f"📧 Would send email to {to_email}: {subject}")
        print(f"   Unsubscribe: {unsubscribe_url}")
        
        # TODO: Implement actual email sending
        # This is where you'd integrate with your email service
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

# Register the blueprint
def register_newsletter_routes(app):
    """Register newsletter routes with the Flask app"""
    app.register_blueprint(newsletter_bp, url_prefix='/newsletter')
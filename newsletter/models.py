"""
Newsletter Models
Simple newsletter subscription and mailing system
"""

from app import db
from datetime import datetime, timezone
from sqlalchemy import JSON
import uuid

class NewsletterSubscriber(db.Model):
    """Newsletter subscribers"""
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    
    # Subscription preferences
    subscribed = db.Column(db.Boolean, default=True)
    preferences = db.Column(JSON)  # Topics they're interested in
    frequency = db.Column(db.String(20), default='weekly')  # weekly, monthly
    
    # Tracking
    subscription_token = db.Column(db.String(100), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmation_sent_at = db.Column(db.DateTime(timezone=True))
    confirmed_at = db.Column(db.DateTime(timezone=True))
    
    # Analytics
    source = db.Column(db.String(100))  # Where they signed up
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Status
    unsubscribed_at = db.Column(db.DateTime(timezone=True))
    bounce_count = db.Column(db.Integer, default=0)
    last_email_sent = db.Column(db.DateTime(timezone=True))
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.subscription_token:
            self.subscription_token = str(uuid.uuid4())

class NewsletterCampaign(db.Model):
    """Newsletter email campaigns"""
    __tablename__ = 'newsletter_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    
    # Content
    content_html = db.Column(db.Text, nullable=False)
    content_text = db.Column(db.Text)  # Plain text version
    
    # Generated content reference
    generated_content_id = db.Column(db.Integer, db.ForeignKey('generated_content.id'))
    
    # Campaign settings
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, sending, sent, cancelled
    send_at = db.Column(db.DateTime(timezone=True))
    
    # Targeting
    target_segments = db.Column(JSON)  # Which subscriber segments to target
    
    # Analytics
    recipients_count = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    delivered_count = db.Column(db.Integer, default=0)
    opened_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    bounced_count = db.Column(db.Integer, default=0)
    unsubscribed_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    sent_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))
    
    # Relationships
    generated_content = db.relationship('GeneratedContent', backref='newsletter_campaigns')
    sends = db.relationship('NewsletterSend', backref='campaign', cascade='all, delete-orphan')

class NewsletterSend(db.Model):
    """Individual email sends (for tracking)"""
    __tablename__ = 'newsletter_sends'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('newsletter_campaigns.id'), nullable=False)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('newsletter_subscribers.id'), nullable=False)
    
    # Email details
    email_address = db.Column(db.String(255), nullable=False)
    message_id = db.Column(db.String(200))  # Email service provider message ID
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, bounced, failed
    
    # Analytics tracking
    sent_at = db.Column(db.DateTime(timezone=True))
    delivered_at = db.Column(db.DateTime(timezone=True))
    opened_at = db.Column(db.DateTime(timezone=True))
    first_click_at = db.Column(db.DateTime(timezone=True))
    
    # Error tracking
    error_message = db.Column(db.Text)
    bounce_reason = db.Column(db.String(200))
    
    # Tracking tokens
    tracking_token = db.Column(db.String(100), unique=True)
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    subscriber = db.relationship('NewsletterSubscriber', backref='email_sends')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.tracking_token:
            self.tracking_token = str(uuid.uuid4())

class NewsletterTemplate(db.Model):
    """Reusable newsletter templates"""
    __tablename__ = 'newsletter_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Template content
    html_template = db.Column(db.Text, nullable=False)
    text_template = db.Column(db.Text)
    
    # Template variables/placeholders
    variables = db.Column(JSON)  # List of available variables
    
    # Settings
    is_default = db.Column(db.Boolean, default=False)
    enabled = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
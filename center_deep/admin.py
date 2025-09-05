from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from .models import db, User, SearchLog, ProxyLog
from .auth import admin_required
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_searches = SearchLog.query.count()
    recent_searches = SearchLog.query.order_by(SearchLog.timestamp.desc()).limit(10).all()
    
    # Get search statistics for last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_searches = db.session.query(
        db.func.date(SearchLog.timestamp).label('date'),
        db.func.count(SearchLog.id).label('count')
    ).filter(SearchLog.timestamp >= seven_days_ago).group_by('date').all()
    
    stats = {
        'total_users': total_users,
        'total_searches': total_searches,
        'recent_searches': recent_searches,
        'daily_searches': daily_searches
    }
    
    return render_template('center_deep/admin/dashboard.html', stats=stats)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """User management"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('center_deep/admin/users.html', users=all_users)

@admin_bp.route('/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin from self
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot modify your own admin status'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({'success': True, 'is_admin': user.is_admin})

@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting self
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/admin/search-logs')
@login_required
@admin_required
def search_logs():
    """View search logs"""
    page = request.args.get('page', 1, type=int)
    logs = SearchLog.query.order_by(SearchLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('center_deep/admin/search_logs.html', logs=logs)

@admin_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """System settings"""
    if request.method == 'POST':
        # Save settings
        settings_data = request.form.to_dict()
        # Here you would save settings to a configuration file or database
        flash('Settings saved successfully', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('center_deep/admin/settings.html')

@admin_bp.route('/admin/analytics')
@login_required
@admin_required
def analytics():
    """Analytics dashboard"""
    # Get search trends
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Most searched queries
    popular_queries = db.session.query(
        SearchLog.query,
        db.func.count(SearchLog.id).label('count')
    ).filter(SearchLog.timestamp >= thirty_days_ago)\
     .group_by(SearchLog.query)\
     .order_by(db.func.count(SearchLog.id).desc())\
     .limit(20).all()
    
    # Search volume by hour
    hourly_searches = db.session.query(
        db.func.strftime('%H', SearchLog.timestamp).label('hour'),
        db.func.count(SearchLog.id).label('count')
    ).filter(SearchLog.timestamp >= thirty_days_ago)\
     .group_by('hour').all()
    
    analytics_data = {
        'popular_queries': popular_queries,
        'hourly_searches': hourly_searches
    }
    
    return render_template('center_deep/admin/analytics.html', analytics=analytics_data)

def init_admin(app):
    """Initialize admin panel"""
    app.register_blueprint(admin_bp)
    return app
"""
Center Deep Integration for SearXNG webapp
This module extends SearXNG with Center Deep features
"""

import os
import sys
from pathlib import Path

# Add Center Deep module to path
center_deep_path = Path(__file__).parent
sys.path.insert(0, str(center_deep_path))

from flask import Flask, request, g, session
from datetime import datetime
from .models import db, SearchLog
from .auth import init_auth, current_user
from .admin import init_admin

def log_search(query, results_count=0, engines_used="", response_time=0):
    """Log search query to database"""
    try:
        log = SearchLog(
            user_id=current_user.id if current_user and current_user.is_authenticated else None,
            query=query,
            timestamp=datetime.utcnow(),
            response_time=response_time,
            results_count=results_count,
            ip_address=request.remote_addr,
            engines_used=engines_used
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging search: {e}")
        db.session.rollback()

def init_center_deep_webapp(app):
    """Initialize Center Deep features in SearXNG webapp"""
    
    # Set up Flask extensions
    app.config['SECRET_KEY'] = os.environ.get('SEARXNG_SECRET', 'change-this-in-production')
    
    # Initialize database
    from .models import init_db
    init_db(app)
    
    # Initialize authentication
    init_auth(app)
    
    # Initialize admin panel
    init_admin(app)
    
    # Add Center Deep context to templates
    @app.context_processor
    def inject_center_deep():
        return {
            'center_deep_enabled': True,
            'current_user': current_user,
            'instance_name': 'Center Deep'
        }
    
    # Hook into search requests
    original_search = None
    if hasattr(app, 'search'):
        original_search = app.search
    
    def center_deep_search(*args, **kwargs):
        """Wrapper for search with Center Deep features"""
        start_time = datetime.utcnow()
        
        # Call original search
        if original_search:
            results = original_search(*args, **kwargs)
        else:
            results = None
        
        # Log the search
        if results and request:
            query = request.args.get('q', '')
            response_time = (datetime.utcnow() - start_time).total_seconds()
            log_search(
                query=query,
                results_count=len(results) if hasattr(results, '__len__') else 0,
                response_time=response_time
            )
        
        return results
    
    if original_search:
        app.search = center_deep_search
    
    print("✅ Center Deep features initialized successfully")
    return app

# Auto-initialize if imported from SearXNG
def auto_init():
    """Auto-initialize when imported"""
    try:
        from searx import webapp
        if hasattr(webapp, 'app'):
            init_center_deep_webapp(webapp.app)
    except ImportError:
        pass

# Run auto-init
auto_init()
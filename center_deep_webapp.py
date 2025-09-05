#!/usr/bin/env python
"""
Center Deep Web Application
Combines Center Deep's GUI with SearXNG's search backend
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Import SearXNG's search functionality
import sys
sys.path.insert(0, '/usr/local/center-deep')
try:
    from searx import settings
    from searx.search import SearchQuery, Search
    from searx.utils import gen_useragent
    from searx.enginelib import load_engines
    from searx.webapp import get_selected_categories
except ImportError:
    # Fallback for local development
    sys.path.insert(0, './searx')
    from searx import settings
    from searx.search import SearchQuery, Search
    from searx.utils import gen_useragent
    from searx.enginelib import load_engines
    from searx.webapp import get_selected_categories

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/center_deep.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize SearXNG engines
load_engines(settings['engines'])

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    searches = db.relationship('SearchLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SearchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    query = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)
    results_count = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))

# Create tables
with app.app_context():
    db.create_all()
    # Create default admin user if not exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@center-deep.com', is_admin=True)
        admin.set_password('CenterDeep2024!')
        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page with Center Deep branding"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Search using SearXNG backend with Center Deep UI"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('index'))
    
    # Use SearXNG's search backend
    try:
        categories = get_selected_categories(request.args, request.form)
    except:
        categories = []
    
    search_query = SearchQuery(
        query=query,
        engines=[],  # Use all enabled engines
        categories=categories,
        lang='en',
        safesearch=0,
        pageno=page,
        time_range=None
    )
    
    search = Search(search_query)
    result_container = search.search()
    
    # Log the search
    if current_user.is_authenticated:
        log = SearchLog(
            user_id=current_user.id,
            query=query,
            timestamp=datetime.utcnow(),
            results_count=len(result_container.get_ordered_results()),
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    
    # Prepare results for Center Deep template
    results = []
    for result in result_container.get_ordered_results():
        results.append({
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'content': result.get('content', ''),
            'engine': result.get('engine', ''),
            'score': result.get('score', 0)
        })
    
    return render_template('search.html', 
                         query=query,
                         results=results,
                         page=page,
                         total_results=len(results))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
@admin_required
def admin():
    """Admin dashboard"""
    total_users = User.query.count()
    total_searches = SearchLog.query.count()
    recent_searches = SearchLog.query.order_by(SearchLog.timestamp.desc()).limit(10).all()
    
    return render_template('admin.html',
                         total_users=total_users,
                         total_searches=total_searches,
                         recent_searches=recent_searches)

@app.route('/preferences')
def preferences():
    """User preferences"""
    return render_template('preferences.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup wizard"""
    setup_file = '/data/.setup_complete'
    if os.path.exists(setup_file):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Save setup configuration
        config = request.form.to_dict()
        
        # Update admin password if provided
        if config.get('admin_password'):
            admin = User.query.filter_by(username='admin').first()
            if admin:
                admin.set_password(config['admin_password'])
                db.session.commit()
        
        # Mark setup as complete
        with open(setup_file, 'w') as f:
            f.write(datetime.utcnow().isoformat())
        
        return redirect(url_for('index'))
    
    return render_template('setup.html')

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
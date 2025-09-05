#!/usr/bin/env python
"""
Center Deep - Beautiful Search Interface
Uses SearXNG as the search backend API
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import requests
import json
from functools import wraps

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///center_deep.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# SearXNG backend configuration
SEARXNG_URL = os.environ.get('SEARXNG_URL', 'http://searxng:8080')
SEARXNG_TIMEOUT = 10

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    user_stats = {}
    if current_user.is_authenticated:
        # Today's searches
        today = datetime.utcnow().date()
        searches_today = db.session.query(SearchLog).filter(
            SearchLog.user_id == current_user.id,
            db.func.date(SearchLog.timestamp) == today
        ).count()
        
        # Total searches
        total_searches = db.session.query(SearchLog).filter(
            SearchLog.user_id == current_user.id
        ).count()
        
        user_stats = {
            'searches_today': searches_today,
            'total_searches': total_searches
        }
    
    return render_template('index.html', 
                         authenticated=current_user.is_authenticated,
                         user_stats=user_stats)

@app.route('/search')
def search():
    """Search using SearXNG backend with Center Deep UI"""
    query = request.args.get('q', '')
    
    # If no query, redirect to homepage
    if not query:
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    categories = request.args.get('categories', '')
    time_range = request.args.get('time_range', '')
    language = request.args.get('language', 'en')
    safesearch = request.args.get('safesearch', '0')
    
    start_time = datetime.utcnow()
    
    # Make search request to SearXNG API
    try:
        params = {
            'q': query,
            'format': 'json',  # Request JSON format
            'pageno': page,
            'safesearch': safesearch,
            'language': language
        }
        
        if categories:
            params['categories'] = categories
        
        if time_range:
            params['time_range'] = time_range
        
        # Call SearXNG API
        response = requests.get(f'{SEARXNG_URL}/search', 
                              params=params, 
                              timeout=SEARXNG_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            suggestions = data.get('suggestions', [])
            answers = data.get('answers', [])
            infoboxes = data.get('infoboxes', [])
        else:
            results = []
            suggestions = []
            answers = []
            infoboxes = []
            
    except Exception as e:
        print(f"Search error: {e}")
        results = []
        suggestions = []
        answers = []
        infoboxes = []
    
    # Calculate response time
    response_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log search if user is authenticated
    if current_user.is_authenticated:
        search_log = SearchLog(
            user_id=current_user.id,
            query=query,
            response_time=response_time,
            results_count=len(results),
            ip_address=request.remote_addr
        )
        db.session.add(search_log)
        db.session.commit()
    
    return render_template('search.html', 
                         query=query,
                         results=results,
                         suggestions=suggestions,
                         answers=answers,
                         infoboxes=infoboxes,
                         page=page,
                         total_results=len(results),
                         response_time=response_time)

@app.route('/api/search')
def api_search():
    """JSON API endpoint for search"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Forward to SearXNG and return JSON
    params = {
        'q': query,
        'format': 'json',
        'pageno': request.args.get('page', 1),
        'safesearch': request.args.get('safesearch', '0'),
        'language': request.args.get('language', 'en')
    }
    
    try:
        response = requests.get(f'{SEARXNG_URL}/search', params=params, timeout=SEARXNG_TIMEOUT)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Search backend error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            return render_template('login.html', error='Invalid username or password')
    
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
    recent_searches = SearchLog.query.order_by(SearchLog.timestamp.desc()).limit(20).all()
    
    # Get search statistics
    today = datetime.utcnow().date()
    searches_today = db.session.query(SearchLog).filter(
        db.func.date(SearchLog.timestamp) == today
    ).count()
    
    return render_template('admin.html',
                         total_users=total_users,
                         total_searches=total_searches,
                         searches_today=searches_today,
                         recent_searches=recent_searches)

@app.route('/preferences')
def preferences():
    """User preferences"""
    return render_template('preferences.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
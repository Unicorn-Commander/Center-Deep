from flask import Flask, render_template, g, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import requests
import json
import redis
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "center_deep.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Redis for statistics (optional, falls back to in-memory if not available)
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
except:
    redis_client = None
    print("Redis not available, using in-memory statistics")

# In-memory statistics fallback
stats_memory = {
    'total_searches': 0,
    'search_history': [],
    'active_users': set(),
    'response_times': []
}

# Settings storage
app_settings = {
    'proxy': {
        'enabled': False,
        'brightdata_url': '',
        'brightdata_username': '',
        'brightdata_password': '',
        'rotation_interval': 300
    },
    'monitoring': {
        'prometheus_enabled': False,
        'prometheus_url': 'http://localhost:9090',
        'grafana_enabled': False,
        'grafana_url': 'http://localhost:3000'
    },
    'searxng': {
        'url': 'http://localhost:8888',
        'timeout': 10,
        'max_results': 20
    }
}

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_changed = db.Column(db.Boolean, default=False)
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

class ProxyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    proxy_url = db.Column(db.String(200))
    status = db.Column(db.String(50))
    rotation_count = db.Column(db.Integer, default=0)

# Create tables
with app.app_context():
    db.create_all()
    # Create default admin user if not exists
    admin = User.query.filter_by(username='ucadmin').first()
    if not admin:
        # Check if there's an old admin user and remove it
        old_admin = User.query.filter_by(username='admin').first()
        if old_admin:
            db.session.delete(old_admin)
        
        admin = User(username='ucadmin', email='admin@center-deep.com', is_admin=True)
        admin.set_password('MagicUnicorn!8-)')
        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Statistics tracking functions
def track_search(query, response_time, results_count):
    """Track search statistics"""
    if redis_client:
        redis_client.incr('total_searches')
        redis_client.lpush('recent_searches', json.dumps({
            'query': query,
            'timestamp': datetime.utcnow().isoformat(),
            'response_time': response_time,
            'user_id': current_user.id if current_user.is_authenticated else None
        }))
        redis_client.ltrim('recent_searches', 0, 999)  # Keep last 1000
        redis_client.zadd('active_users', {str(request.remote_addr): datetime.utcnow().timestamp()})
    else:
        stats_memory['total_searches'] += 1
        stats_memory['search_history'].append({
            'query': query,
            'timestamp': datetime.utcnow(),
            'response_time': response_time
        })
        stats_memory['active_users'].add(request.remote_addr)
        stats_memory['response_times'].append(response_time)

def get_statistics():
    """Get current statistics"""
    if redis_client:
        total_searches = redis_client.get('total_searches') or 0
        active_users = redis_client.zcount('active_users', 
                                         datetime.utcnow().timestamp() - 86400,
                                         datetime.utcnow().timestamp())
        recent_searches = redis_client.lrange('recent_searches', 0, 10)
    else:
        total_searches = stats_memory['total_searches']
        active_users = len(stats_memory['active_users'])
        recent_searches = stats_memory['search_history'][-10:]
    
    # Calculate average response time from database
    avg_response = db.session.query(db.func.avg(SearchLog.response_time)).scalar() or 0
    
    return {
        'total_searches': int(total_searches),
        'active_users': active_users,
        'avg_response_time': round(avg_response, 2),
        'recent_searches': recent_searches
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    categories = request.args.get('categories', '')
    time_range = request.args.get('time_range', '')
    language = request.args.get('language', '')
    safesearch = request.args.get('safesearch', '0')  # Default to off
    
    if query:
        start_time = datetime.utcnow()
        
        # Make search request to SearXNG
        try:
            searx_url = app_settings['searxng']['url']
            params = {
                'q': query,
                'format': 'json',
                'pageno': page,
                'safesearch': safesearch
            }
            
            # Add category filter
            if categories:
                params['categories'] = categories
            
            # Add time range filter    
            if time_range:
                params['time_range'] = time_range
                
            # Add language filter
            if language:
                params['language'] = language
            
            # Use proxy if enabled
            proxies = None
            if app_settings['proxy']['enabled'] and app_settings['proxy']['brightdata_url']:
                proxies = {
                    'http': app_settings['proxy']['brightdata_url'],
                    'https': app_settings['proxy']['brightdata_url']
                }
                auth = (app_settings['proxy']['brightdata_username'], 
                       app_settings['proxy']['brightdata_password'])
                response = requests.get(searx_url + '/search', params=params, 
                                      proxies=proxies, auth=auth,
                                      timeout=app_settings['searxng']['timeout'])
            else:
                response = requests.get(searx_url + '/search', params=params, 
                                      timeout=app_settings['searxng']['timeout'])
            
            results = response.json() if response.status_code == 200 else {'results': []}
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log search
            search_log = SearchLog(
                user_id=current_user.id if current_user.is_authenticated else None,
                query=query,
                response_time=response_time,
                results_count=len(results.get('results', [])),
                ip_address=request.remote_addr
            )
            db.session.add(search_log)
            db.session.commit()
            
            # Track statistics
            track_search(query, response_time, len(results.get('results', [])))
            
        except Exception as e:
            print(f"Search error: {e}")
            results = {'results': [], 'error': 'Search service unavailable'}
    else:
        results = {'results': []}
    
    return render_template('search.html', query=query, results=results, page=page)

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '')
    suggestions = []
    if query:
        # Get suggestions from recent searches
        recent = SearchLog.query.filter(
            SearchLog.query.like(f'{query}%')
        ).distinct().limit(5).all()
        suggestions = [s.query for s in recent]
        
        # Add default suggestions
        suggestions.extend([
            query + ' news',
            query + ' reddit',
            query + ' wikipedia'
        ])
    return jsonify(list(set(suggestions))[:8])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin' if user.is_admin else 'index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    # Check if any admin user hasn't changed default password
    admin_user = User.query.filter_by(username='ucadmin').first()
    show_default_message = admin_user and not admin_user.password_changed
    
    return render_template('login.html', show_default_message=show_default_message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/preferences')
def preferences():
    return render_template('preferences.html')

@app.route('/admin')
@admin_required
def admin():
    stats = get_statistics()
    return render_template('admin.html', stats=stats)

@app.route('/api/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        data = request.get_json()
        section = data.get('section')
        settings = data.get('data')
        
        # Update settings
        if section in app_settings:
            app_settings[section].update(settings)
            
            # Log proxy changes
            if section == 'proxy' and settings.get('enabled'):
                proxy_log = ProxyLog(
                    proxy_url=settings.get('brightdata_url'),
                    status='enabled'
                )
                db.session.add(proxy_log)
                db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Settings saved'})
    
    return jsonify(app_settings)

@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    """Get real-time statistics"""
    stats = get_statistics()
    
    # Get recent activity
    recent_logs = SearchLog.query.order_by(SearchLog.timestamp.desc()).limit(10).all()
    recent_activity = []
    for log in recent_logs:
        recent_activity.append({
            'time': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'query': log.query,
            'user': log.user.username if log.user else 'Anonymous',
            'response_time': log.response_time
        })
    
    # Get proxy status
    proxy_status = 'inactive'
    if app_settings['proxy']['enabled']:
        proxy_status = 'active'
    
    return jsonify({
        'total_searches': stats['total_searches'],
        'active_users': stats['active_users'],
        'avg_response_time': stats['avg_response_time'],
        'proxy_status': proxy_status,
        'recent_activity': recent_activity
    })

@app.route('/api/admin/change-password', methods=['POST'])
@admin_required
def change_password():
    """Change admin password"""
    data = request.get_json() or request.form
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new passwords required'}), 400
    
    # Verify current password
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Update password
    current_user.set_password(new_password)
    current_user.password_changed = True
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Password changed successfully'})

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users"""
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
        })
    return jsonify(user_list)

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    data = request.get_json() or request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create user
    user = User(username=username, email=email, is_admin=bool(is_admin))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'User created successfully'})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting the current admin
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'User deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8890, debug=True)
"""
Center Deep - Open Source Privacy-First Metasearch Engine
MIT Licensed - Free for everyone
"""

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
import markdown
import subprocess
import docker

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
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = int(os.environ.get('REDIS_PORT', 6379))
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    redis_client.ping()
    print(f"Connected to Redis at {redis_host}:{redis_port}")
except:
    redis_client = None
    print("Redis not available, using in-memory statistics")

# Initialize Docker client for container management
try:
    docker_client = docker.from_env()
    print("Docker client initialized")
except:
    docker_client = None
    print("Docker not available, container management disabled")

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SearchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    results_count = db.Column(db.Integer)
    response_time = db.Column(db.Float)

class ProxyConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    enabled = db.Column(db.Boolean, default=False)
    provider = db.Column(db.String(50), default='brightdata')
    url = db.Column(db.String(200))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    rotation_interval = db.Column(db.Integer, default=300)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ToolServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200))
    port = db.Column(db.Integer)
    container_name = db.Column(db.String(100))
    enabled = db.Column(db.Boolean, default=False)
    llm_model = db.Column(db.String(50))
    api_base = db.Column(db.String(200))
    api_key = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    """Main search page"""
    return render_template('index.html')

@app.route('/search')
def search():
    """Search results page"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    # Log the search (privacy-respecting - no personal data by default)
    if current_user.is_authenticated:
        log = SearchLog(
            query=query,
            user_id=current_user.id,
            ip_address=request.remote_addr,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    
    # Update statistics
    if redis_client:
        redis_client.incr('total_searches')
        redis_client.hincrby('search_queries', query, 1)
        redis_client.zadd('recent_searches', {query: datetime.utcnow().timestamp()})
    
    return render_template('search.html', query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
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
    """User logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    """Admin dashboard"""
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Get statistics
    stats = {
        'total_searches': 0,
        'total_users': User.query.count(),
        'recent_searches': [],
        'popular_queries': []
    }
    
    if redis_client:
        stats['total_searches'] = redis_client.get('total_searches') or 0
        
        # Get recent searches
        recent = redis_client.zrevrange('recent_searches', 0, 9, withscores=True)
        stats['recent_searches'] = [(q, datetime.fromtimestamp(s)) for q, s in recent]
        
        # Get popular queries
        popular = redis_client.hgetall('search_queries')
        if popular:
            sorted_popular = sorted(popular.items(), key=lambda x: int(x[1]), reverse=True)[:10]
            stats['popular_queries'] = sorted_popular
    
    # Get proxy configuration
    proxy_config = ProxyConfig.query.first()
    
    # Get tool servers status
    tool_servers = ToolServer.query.all()
    
    # Check Docker container status
    if docker_client:
        for tool in tool_servers:
            try:
                container = docker_client.containers.get(tool.container_name)
                tool.status = container.status
            except:
                tool.status = 'not_found'
    
    return render_template('admin.html', 
                         stats=stats, 
                         proxy_config=proxy_config,
                         tool_servers=tool_servers)

@app.route('/api/proxy', methods=['GET', 'POST'])
@login_required
def api_proxy():
    """API endpoint for proxy configuration"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        data = request.json
        
        proxy_config = ProxyConfig.query.first()
        if not proxy_config:
            proxy_config = ProxyConfig()
            db.session.add(proxy_config)
        
        proxy_config.enabled = data.get('enabled', False)
        proxy_config.url = data.get('url', '')
        proxy_config.username = data.get('username', '')
        proxy_config.password = data.get('password', '')
        proxy_config.rotation_interval = data.get('rotation_interval', 300)
        proxy_config.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Proxy configuration updated'})
    
    proxy_config = ProxyConfig.query.first()
    if proxy_config:
        return jsonify({
            'enabled': proxy_config.enabled,
            'url': proxy_config.url,
            'username': proxy_config.username,
            'rotation_interval': proxy_config.rotation_interval
        })
    
    return jsonify({'enabled': False})

@app.route('/api/toolserver/<int:server_id>', methods=['POST'])
@login_required
def api_toolserver(server_id):
    """Control tool servers"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not docker_client:
        return jsonify({'error': 'Docker not available'}), 503
    
    action = request.json.get('action')
    tool_server = ToolServer.query.get(server_id)
    
    if not tool_server:
        return jsonify({'error': 'Tool server not found'}), 404
    
    try:
        if action == 'start':
            # Start the container
            container = docker_client.containers.get(tool_server.container_name)
            container.start()
            tool_server.enabled = True
            db.session.commit()
            return jsonify({'success': True, 'message': f'{tool_server.name} started'})
        
        elif action == 'stop':
            # Stop the container
            container = docker_client.containers.get(tool_server.container_name)
            container.stop()
            tool_server.enabled = False
            db.session.commit()
            return jsonify({'success': True, 'message': f'{tool_server.name} stopped'})
        
        elif action == 'restart':
            # Restart the container
            container = docker_client.containers.get(tool_server.container_name)
            container.restart()
            return jsonify({'success': True, 'message': f'{tool_server.name} restarted'})
        
        elif action == 'logs':
            # Get container logs
            container = docker_client.containers.get(tool_server.container_name)
            logs = container.logs(tail=100).decode('utf-8')
            return jsonify({'success': True, 'logs': logs})
    
    except docker.errors.NotFound:
        return jsonify({'error': 'Container not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid action'}), 400

@app.route('/api/stats')
def api_stats():
    """Get search statistics"""
    stats = {
        'total_searches': 0,
        'recent_searches': []
    }
    
    if redis_client:
        stats['total_searches'] = redis_client.get('total_searches') or 0
        
        # Get recent searches (last 10)
        recent = redis_client.zrevrange('recent_searches', 0, 9)
        stats['recent_searches'] = recent
    
    return jsonify(stats)

@app.route('/preferences')
def preferences():
    """User preferences page"""
    return render_template('preferences.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# Initialize database
def init_db():
    """Initialize database with default data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@center-deep.local',
                is_admin=True
            )
            admin.set_password('changeme')
            db.session.add(admin)
        
        # Initialize tool servers
        tool_servers = [
            {
                'name': 'Search Tool',
                'description': 'Basic search tool for web, GitHub, Reddit',
                'port': 8001,
                'container_name': 'center-deep-tool-search'
            },
            {
                'name': 'Deep Search',
                'description': 'Multi-level search with link following',
                'port': 8002,
                'container_name': 'center-deep-tool-deep-search'
            },
            {
                'name': 'Report Generator',
                'description': 'Professional report creation',
                'port': 8003,
                'container_name': 'center-deep-tool-report'
            },
            {
                'name': 'Academic Research',
                'description': 'Academic paper generation',
                'port': 8004,
                'container_name': 'center-deep-tool-academic'
            }
        ]
        
        for tool_data in tool_servers:
            tool = ToolServer.query.filter_by(name=tool_data['name']).first()
            if not tool:
                tool = ToolServer(**tool_data)
                db.session.add(tool)
        
        db.session.commit()
        print("Database initialized successfully")

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    
    # Run the application
    port = int(os.environ.get('PORT', 8890))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
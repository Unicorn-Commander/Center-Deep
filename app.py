from flask import Flask, render_template, g, request, jsonify, redirect, url_for, session, flash
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

# Redis connection for search caching only (analytics disabled in free version)
try:
    # Check if using external Redis
    use_external_redis = os.environ.get('USE_EXTERNAL_REDIS', 'false').lower() == 'true'
    
    if use_external_redis:
        # Use external Redis configuration
        redis_host = os.environ.get('EXTERNAL_REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('EXTERNAL_REDIS_PORT', 6379))
        redis_db = int(os.environ.get('EXTERNAL_REDIS_DB', 0))
        redis_password = os.environ.get('EXTERNAL_REDIS_PASSWORD', None)
        print(f"📡 Connecting to external Redis at {redis_host}:{redis_port}/{redis_db}")
    else:
        # Use internal Redis (Docker container)
        redis_host = os.environ.get('REDIS_HOST', 'redis-search')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        redis_db = 0
        redis_password = None
        print(f"📡 Connecting to internal Redis at {redis_host}:{redis_port}")
    
    redis_client = redis.Redis(
        host=redis_host, 
        port=redis_port, 
        db=redis_db, 
        password=redis_password,
        decode_responses=True
    )
    redis_client.ping()
    print(f"✅ Redis connected successfully to {redis_host}:{redis_port}/{redis_db}")
except Exception as e:
    redis_client = None
    print(f"❌ Redis not available ({e}), search caching disabled")

# Settings storage
app_settings = {
    'proxy': {
        'enabled': False,
        'brightdata_url': '',
        'brightdata_username': '',
        'brightdata_password': '',
        'rotation_interval': 300
    },
    'searxng': {
        'url': os.environ.get('SEARXNG_BACKEND_URL', 'http://localhost:8080'),
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


# Check if setup is complete
def is_setup_complete():
    """Check if initial setup has been completed"""
    setup_file = os.path.join(os.path.dirname(__file__), '.setup_complete')
    return os.path.exists(setup_file) or os.environ.get('SETUP_COMPLETE', '').lower() == 'true'

def save_configuration(config_data):
    """Save configuration from setup wizard"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    # Read existing .env if it exists
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Update with new configuration
    env_vars.update({
        'ADMIN_USERNAME': config_data.get('admin_username', 'admin'),
        'ADMIN_PASSWORD': config_data.get('admin_password', ''),
        'SECRET_KEY': config_data.get('secret_key', os.urandom(24).hex()),
        'INSTANCE_NAME': config_data.get('instance_name', 'Center Deep'),
        'DEFAULT_THEME': config_data.get('default_theme', 'magic-unicorn'),
        'INFINITE_SCROLL': str(config_data.get('infinite_scroll', True)),
        'IMAGE_PROXY': str(config_data.get('image_proxy', True)),
        'AUTOCOMPLETE': str(config_data.get('autocomplete', True)),
        'SAFESEARCH': config_data.get('safesearch', '0'),
        'USE_EXTERNAL_REDIS': 'false',
        'REDIS_HOST': config_data.get('redis_host', 'center-deep-redis'),
        'REDIS_PORT': config_data.get('redis_port', '6385'),
        'SETUP_COMPLETE': 'true'
    })
    
    # Write updated configuration
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f'{key}={value}\n')
    
    # Mark setup as complete
    setup_file = os.path.join(os.path.dirname(__file__), '.setup_complete')
    with open(setup_file, 'w') as f:
        f.write(datetime.utcnow().isoformat())
    
    # Update SearXNG configuration with selected engines
    update_searxng_engines(config_data.get('engines', []))

def update_searxng_engines(selected_engines):
    """Update SearXNG settings with selected engines"""
    # This would update the searxng/settings.yml file
    # For now, we'll just log the selection
    print(f"Selected engines: {selected_engines}")

# Routes
@app.route('/health')
def health():
    """Health check endpoint for Docker"""
    return jsonify({'status': 'healthy', 'service': 'Center Deep'}), 200

@app.route('/')
def index():
    # Check if setup is complete
    if not is_setup_complete():
        return redirect(url_for('setup'))
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup wizard"""
    # If setup is already complete, redirect to home
    if is_setup_complete():
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Process setup form
        config_data = {
            'admin_username': request.form.get('admin_username'),
            'admin_password': generate_password_hash(request.form.get('admin_password')),
            'admin_email': request.form.get('admin_email'),
            'instance_name': request.form.get('instance_name', 'Center Deep'),
            'engines': request.form.getlist('engines'),
            'safesearch': request.form.get('safesearch', '0'),
            'default_theme': request.form.get('default_theme', 'magic-unicorn'),
            'infinite_scroll': request.form.get('infinite_scroll') == 'on',
            'image_proxy': request.form.get('image_proxy') == 'on',
            'autocomplete': request.form.get('autocomplete') == 'on',
            'secret_key': request.form.get('secret_key', os.urandom(24).hex()),
            'redis_host': request.form.get('redis_host', 'center-deep-redis'),
            'redis_port': request.form.get('redis_port', '6385')
        }
        
        # Save configuration
        save_configuration(config_data)
        
        # Create admin user in database
        admin_user = User.query.filter_by(username=config_data['admin_username']).first()
        if not admin_user:
            admin_user = User(
                username=config_data['admin_username'],
                email=config_data.get('admin_email'),
                password_hash=config_data['admin_password'],
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
        
        flash('🎉 Setup complete! Your private search engine is ready.', 'success')
        # Go directly to the main search page after setup
        return redirect(url_for('index'))
    
    # Generate a secret key for the session
    secret_key = os.urandom(24).hex()
    return render_template('setup.html', secret_key=secret_key)

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
        
        # Use internal search engine (no external SearXNG dependency)
        try:
            from search_engine import perform_search
            
            # Perform search using our integrated engine
            results = perform_search(
                query=query,
                categories=categories,
                page=page,
                safesearch=safesearch,
                time_range=time_range,
                language=language
            )
            
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
    return render_template('admin.html')

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

# LLM Configuration Routes
@app.route('/api/admin/llm/providers', methods=['GET', 'POST'])
@admin_required
def manage_llm_providers():
    """Manage LLM providers"""
    if request.method == 'POST':
        data = request.get_json()
        
        # Check if provider exists
        existing = db.session.query(db.Table('llm_providers')).filter_by(name=data['name']).first() if db.metadata.tables.get('llm_providers') else None
        if existing:
            return jsonify({'error': 'Provider with this name already exists'}), 400
        
        # Import model from toolserver
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'toolserver'))
        from toolserver.main import LLMProvider
        
        provider = LLMProvider(
            name=data['name'],
            api_base=data['api_base'],
            api_key=data.get('api_key', ''),
            model_name=data['model_name'],
            enabled=data.get('enabled', True)
        )
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'LLM provider added successfully'})
    
    # GET request - return all providers
    from toolserver.main import LLMProvider
    providers = LLMProvider.query.all()
    provider_list = []
    for provider in providers:
        provider_list.append({
            'id': provider.id,
            'name': provider.name,
            'api_base': provider.api_base,
            'model_name': provider.model_name,
            'enabled': provider.enabled,
            'created_at': provider.created_at.strftime('%Y-%m-%d %H:%M:%S') if provider.created_at else None
        })
    
    return jsonify(provider_list)

@app.route('/api/admin/llm/providers/<int:provider_id>/toggle', methods=['POST'])
@admin_required
def toggle_llm_provider(provider_id):
    """Toggle LLM provider status"""
    from toolserver.main import LLMProvider
    provider = LLMProvider.query.get_or_404(provider_id)
    provider.enabled = not provider.enabled
    db.session.commit()
    return jsonify({'status': 'success', 'enabled': provider.enabled})

@app.route('/api/admin/llm/providers/<int:provider_id>', methods=['DELETE'])
@admin_required
def delete_llm_provider(provider_id):
    """Delete LLM provider"""
    from toolserver.main import LLMProvider
    provider = LLMProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Provider deleted successfully'})

@app.route('/api/admin/embedding/providers', methods=['GET', 'POST'])
@admin_required
def manage_embedding_providers():
    """Manage embedding providers"""
    from toolserver.main import EmbeddingProvider
    
    if request.method == 'POST':
        data = request.get_json()
        
        provider = EmbeddingProvider(
            name=data['name'],
            api_base=data['api_base'],
            api_key=data.get('api_key', ''),
            model_name=data['model_name'],
            dimension=data.get('dimension', 1536),
            enabled=data.get('enabled', True)
        )
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Embedding provider added successfully'})
    
    # GET request - return all providers
    providers = EmbeddingProvider.query.all()
    provider_list = []
    for provider in providers:
        provider_list.append({
            'id': provider.id,
            'name': provider.name,
            'api_base': provider.api_base,
            'model_name': provider.model_name,
            'dimension': provider.dimension,
            'enabled': provider.enabled,
            'created_at': provider.created_at.strftime('%Y-%m-%d %H:%M:%S') if provider.created_at else None
        })
    
    return jsonify(provider_list)

@app.route('/api/admin/embedding/providers/<int:provider_id>/toggle', methods=['POST'])
@admin_required
def toggle_embedding_provider(provider_id):
    """Toggle embedding provider status"""
    from toolserver.main import EmbeddingProvider
    provider = EmbeddingProvider.query.get_or_404(provider_id)
    provider.enabled = not provider.enabled
    db.session.commit()
    return jsonify({'status': 'success', 'enabled': provider.enabled})

@app.route('/api/admin/embedding/providers/<int:provider_id>', methods=['DELETE'])
@admin_required
def delete_embedding_provider(provider_id):
    """Delete embedding provider"""
    from toolserver.main import EmbeddingProvider
    provider = EmbeddingProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Provider deleted successfully'})

@app.route('/api/admin/reranker/providers', methods=['GET', 'POST'])
@admin_required
def manage_reranker_providers():
    """Manage reranker providers"""
    from toolserver.main import RerankerProvider
    
    if request.method == 'POST':
        data = request.get_json()
        
        provider = RerankerProvider(
            name=data['name'],
            api_base=data['api_base'],
            api_key=data.get('api_key', ''),
            model_name=data['model_name'],
            top_k=data.get('top_k', 10),
            enabled=data.get('enabled', True)
        )
        db.session.add(provider)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Reranker provider added successfully'})
    
    # GET request - return all providers
    providers = RerankerProvider.query.all()
    provider_list = []
    for provider in providers:
        provider_list.append({
            'id': provider.id,
            'name': provider.name,
            'api_base': provider.api_base,
            'model_name': provider.model_name,
            'top_k': provider.top_k,
            'enabled': provider.enabled,
            'created_at': provider.created_at.strftime('%Y-%m-%d %H:%M:%S') if provider.created_at else None
        })
    
    return jsonify(provider_list)

@app.route('/api/admin/reranker/providers/<int:provider_id>/toggle', methods=['POST'])
@admin_required
def toggle_reranker_provider(provider_id):
    """Toggle reranker provider status"""
    from toolserver.main import RerankerProvider
    provider = RerankerProvider.query.get_or_404(provider_id)
    provider.enabled = not provider.enabled
    db.session.commit()
    return jsonify({'status': 'success', 'enabled': provider.enabled})

@app.route('/api/admin/reranker/providers/<int:provider_id>', methods=['DELETE'])
@admin_required
def delete_reranker_provider(provider_id):
    """Delete reranker provider"""
    from toolserver.main import RerankerProvider
    provider = RerankerProvider.query.get_or_404(provider_id)
    db.session.delete(provider)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Provider deleted successfully'})

@app.route('/api/admin/llm/tool-config', methods=['GET', 'POST'])
@admin_required
def manage_tool_llm_config():
    """Manage tool LLM configurations"""
    from toolserver.main import ToolLLMConfig
    
    if request.method == 'POST':
        data = request.get_json()
        configs = data.get('configs', [])
        
        for config_data in configs:
            # Find existing config or create new
            config = ToolLLMConfig.query.filter_by(
                tool_name=config_data['tool_name']
            ).first()
            
            if not config:
                config = ToolLLMConfig(tool_name=config_data['tool_name'])
                db.session.add(config)
            
            # Update config
            config.llm_provider_id = config_data.get('llm_provider_id') or None
            config.embedding_provider_id = config_data.get('embedding_provider_id') or None
            config.reranker_provider_id = config_data.get('reranker_provider_id') or None
            config.temperature = config_data.get('temperature', 0.7)
            config.max_tokens = config_data.get('max_tokens', 4000)
            config.enabled = True
            config.purpose = f"LLM for {config_data['tool_name'].replace('_', ' ').title()}"
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Tool LLM configurations saved'})
    
    # GET request - return all configurations
    configs = ToolLLMConfig.query.all()
    config_list = []
    for config in configs:
        config_list.append({
            'id': config.id,
            'tool_name': config.tool_name,
            'purpose': config.purpose,
            'llm_provider_id': config.llm_provider_id,
            'embedding_provider_id': config.embedding_provider_id,
            'reranker_provider_id': config.reranker_provider_id,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'enabled': config.enabled
        })
    
    return jsonify(config_list)

# Tool Server Management Routes
@app.route('/api/admin/tool-servers/status')
@admin_required
def get_tool_servers_status():
    """Get status of all tool servers"""
    import subprocess
    import json
    
    statuses = {}
    tool_servers = ['search', 'deep-search', 'report', 'academic']
    
    for server in tool_servers:
        container_name = f'center-deep-tool-{server}'
        try:
            # Check if container exists and is running
            result = subprocess.run(
                ['docker', 'inspect', container_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                container_info = json.loads(result.stdout)[0]
                is_running = container_info['State']['Running']
                statuses[server] = {
                    'status': 'running' if is_running else 'stopped',
                    'running': is_running,
                    'container': container_name,
                    'started_at': container_info['State'].get('StartedAt', ''),
                    'health': container_info['State'].get('Health', {}).get('Status', 'unknown')
                }
            else:
                statuses[server] = {
                    'status': 'not_found',
                    'running': False,
                    'container': container_name
                }
        except Exception as e:
            statuses[server] = {
                'status': 'error',
                'running': False,
                'error': str(e)
            }
    
    return jsonify(statuses)

@app.route('/api/admin/tool-servers/<server_id>/start', methods=['POST'])
@admin_required
def start_tool_server(server_id):
    """Start a tool server"""
    import subprocess
    
    if server_id not in ['search', 'deep-search', 'report', 'academic']:
        return jsonify({'error': 'Invalid server ID'}), 400
    
    try:
        # Get LLM configuration for this tool
        from toolserver.main import ToolLLMConfig, LLMProvider
        
        tool_name = server_id.replace('-', '_')
        config = ToolLLMConfig.query.filter_by(
            tool_name=tool_name,
            enabled=True
        ).first()
        
        env_vars = []
        if config and config.llm_provider:
            provider = config.llm_provider
            env_vars = [
                '-e', f'{tool_name.upper()}_LLM_API_BASE={provider.api_base}',
                '-e', f'{tool_name.upper()}_LLM_API_KEY={provider.api_key}',
                '-e', f'{tool_name.upper()}_LLM_MODEL={provider.model_name}'
            ]
        
        # Start the container
        cmd = [
            'docker-compose', 
            '-f', 'docker-compose.tools.yml',
            'up', '-d',
            f'tool-{server_id}'
        ]
        
        if env_vars:
            # Set environment variables
            import os
            for i in range(0, len(env_vars), 2):
                key = env_vars[i+1].split('=')[0]
                value = env_vars[i+1].split('=')[1]
                os.environ[key] = value
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Tool server started'})
        else:
            return jsonify({'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/tool-servers/<server_id>/stop', methods=['POST'])
@admin_required
def stop_tool_server(server_id):
    """Stop a tool server"""
    import subprocess
    
    if server_id not in ['search', 'deep-search', 'report', 'academic']:
        return jsonify({'error': 'Invalid server ID'}), 400
    
    try:
        container_name = f'center-deep-tool-{server_id}'
        result = subprocess.run(
            ['docker', 'stop', container_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Tool server stopped'})
        else:
            return jsonify({'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/tool-servers/<server_id>/restart', methods=['POST'])
@admin_required
def restart_tool_server(server_id):
    """Restart a tool server"""
    import subprocess
    
    if server_id not in ['search', 'deep-search', 'report', 'academic']:
        return jsonify({'error': 'Invalid server ID'}), 400
    
    try:
        container_name = f'center-deep-tool-{server_id}'
        
        # Stop container
        subprocess.run(['docker', 'stop', container_name], capture_output=True)
        
        # Start it again
        result = subprocess.run([
            'docker-compose',
            '-f', 'docker-compose.tools.yml',
            'up', '-d',
            f'tool-{server_id}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Tool server restarted'})
        else:
            return jsonify({'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/tool-servers/<server_id>/logs')
@admin_required
def get_tool_server_logs(server_id):
    """Get tool server logs"""
    import subprocess
    
    if server_id not in ['search', 'deep-search', 'report', 'academic']:
        return jsonify({'error': 'Invalid server ID'}), 400
    
    try:
        container_name = f'center-deep-tool-{server_id}'
        result = subprocess.run(
            ['docker', 'logs', '--tail', '100', container_name],
            capture_output=True,
            text=True
        )
        
        return f'''
        <html>
        <head>
            <title>{server_id} Logs</title>
            <style>
                body {{ 
                    background: #0d1117; 
                    color: #e8eaf6; 
                    font-family: monospace; 
                    padding: 20px;
                    white-space: pre-wrap;
                }}
                h1 {{ color: #00bcd4; }}
            </style>
        </head>
        <body>
            <h1>Tool Server Logs: {server_id}</h1>
            <pre>{result.stdout}\n{result.stderr}</pre>
        </body>
        </html>
        '''
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Blog and Newsletter systems removed (out of scope for Center Deep)
# These features are available in Center Deep Pro

# Add markdown filter for templates
@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown text to HTML"""
    if text:
        return markdown.markdown(text, extensions=['codehilite', 'fenced_code'])
    return ""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8890))
    app.run(host='0.0.0.0', port=port, debug=True)
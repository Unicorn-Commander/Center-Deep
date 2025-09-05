"""
Center Deep Plugin - Adds user management and admin features to SearXNG
"""
from flask import request, render_template_string, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

# Simple in-memory storage for demo (use database in production)
users_db = {}
search_logs = []
admin_user = {'username': 'admin', 'password': generate_password_hash('CenterDeep2024!')}

# Template for login page
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html class="theme-magic-unicorn">
<head>
    <title>Center Deep - Login</title>
    <link rel="stylesheet" href="/static/themes/simple/css/theme-magic-unicorn.css">
    <style>
        .login-container { max-width: 400px; margin: 100px auto; padding: 2rem; 
                          background: var(--card-bg); border-radius: 12px; }
        .login-form { display: flex; flex-direction: column; gap: 1rem; }
        .login-input { padding: 0.75rem; background: rgba(255,255,255,0.1); 
                      border: 1px solid var(--border); border-radius: 8px; color: white; }
        .login-button { padding: 0.75rem; background: var(--gradient-magic); 
                       border: none; border-radius: 8px; color: white; font-weight: bold; }
        .logo { text-align: center; margin-bottom: 2rem; 
               background: var(--gradient-magic); -webkit-background-clip: text; 
               -webkit-text-fill-color: transparent; }
    </style>
</head>
<body style="background: var(--gradient-dark);">
    <div class="login-container">
        <h1 class="logo">Center Deep</h1>
        {% if error %}
            <div style="color: #ff6b6b; margin-bottom: 1rem;">{{ error }}</div>
        {% endif %}
        <form class="login-form" method="POST">
            <input class="login-input" type="text" name="username" placeholder="Username" required>
            <input class="login-input" type="password" name="password" placeholder="Password" required>
            <button class="login-button" type="submit">Login</button>
        </form>
        <p style="text-align: center; margin-top: 1rem; color: var(--text-secondary);">
            <a href="/" style="color: var(--text-link);">← Back to Search</a>
        </p>
    </div>
</body>
</html>
'''

# Template for admin dashboard
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html class="theme-magic-unicorn">
<head>
    <title>Center Deep - Admin Dashboard</title>
    <link rel="stylesheet" href="/static/themes/simple/css/theme-magic-unicorn.css">
    <style>
        .admin-container { max-width: 1200px; margin: 2rem auto; padding: 2rem; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .dashboard-card { background: var(--card-bg); padding: 2rem; border-radius: 12px; 
                         border: 1px solid var(--border); }
        .stat-number { font-size: 2rem; font-weight: bold; color: var(--primary); }
        .recent-searches { max-height: 400px; overflow-y: auto; }
        .search-item { padding: 0.5rem; margin: 0.5rem 0; background: rgba(255,255,255,0.05); 
                      border-radius: 8px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .logout-btn { padding: 0.5rem 1rem; background: var(--danger); color: white; 
                     text-decoration: none; border-radius: 8px; }
    </style>
</head>
<body style="background: var(--gradient-dark); color: var(--text-primary);">
    <div class="admin-container">
        <div class="header">
            <h1>🦄 Center Deep Admin Dashboard</h1>
            <div>
                <a href="/" style="margin-right: 1rem; color: var(--text-link);">Search</a>
                <a href="/center_deep/logout" class="logout-btn">Logout</a>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <h3>📊 Search Statistics</h3>
                <div class="stat-number">{{ total_searches }}</div>
                <p>Total Searches Today</p>
            </div>
            
            <div class="dashboard-card">
                <h3>👥 Users</h3>
                <div class="stat-number">{{ total_users }}</div>
                <p>Registered Users</p>
            </div>
            
            <div class="dashboard-card">
                <h3>🔍 Recent Searches</h3>
                <div class="recent-searches">
                    {% for search in recent_searches %}
                    <div class="search-item">
                        <strong>{{ search.query }}</strong>
                        <br><small>{{ search.timestamp }} - {{ search.results }} results</small>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3>🚀 Quick Actions</h3>
                <p><a href="/stats" style="color: var(--text-link);">View Engine Stats</a></p>
                <p><a href="/preferences" style="color: var(--text-link);">System Preferences</a></p>
                <p><a href="/center_deep/api" style="color: var(--text-link);">API Documentation</a></p>
            </div>
        </div>
    </div>
</body>
</html>
'''

def init_center_deep_plugin(app):
    """Initialize Center Deep plugin routes"""
    
    @app.route('/center_deep/login', methods=['GET', 'POST'])
    def center_deep_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == 'admin' and check_password_hash(admin_user['password'], password):
                session['center_deep_admin'] = True
                session['center_deep_user'] = username
                return redirect('/center_deep/admin')
            else:
                return render_template_string(LOGIN_TEMPLATE, error='Invalid credentials')
        
        return render_template_string(LOGIN_TEMPLATE)
    
    @app.route('/center_deep/logout')
    def center_deep_logout():
        session.pop('center_deep_admin', None)
        session.pop('center_deep_user', None)
        return redirect('/')
    
    @app.route('/center_deep/admin')
    def center_deep_admin():
        if not session.get('center_deep_admin'):
            return redirect('/center_deep/login')
        
        # Mock statistics (replace with real data)
        stats = {
            'total_searches': len(search_logs),
            'total_users': len(users_db) + 1,  # +1 for admin
            'recent_searches': [
                {'query': 'python programming', 'timestamp': '2 mins ago', 'results': 150},
                {'query': 'machine learning', 'timestamp': '5 mins ago', 'results': 89},
                {'query': 'web development', 'timestamp': '12 mins ago', 'results': 234},
                {'query': 'data science', 'timestamp': '18 mins ago', 'results': 167},
            ]
        }
        
        return render_template_string(ADMIN_TEMPLATE, **stats)
    
    @app.route('/center_deep/api')
    def center_deep_api_docs():
        """API documentation"""
        return jsonify({
            'name': 'Center Deep API',
            'version': '2.0.0',
            'endpoints': {
                '/search?format=json': 'Search with JSON response',
                '/center_deep/login': 'Admin login',
                '/center_deep/admin': 'Admin dashboard',
                '/center_deep/api': 'API documentation'
            },
            'features': [
                '250+ search engines',
                'Purple gradient UI',
                'Magic unicorn theme',
                'Admin dashboard',
                'User management',
                'Search analytics'
            ]
        })
    
    # Add admin link to navigation
    @app.context_processor
    def inject_center_deep_vars():
        return {
            'is_center_deep_admin': session.get('center_deep_admin', False)
        }

    return app
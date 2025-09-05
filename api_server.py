#!/usr/bin/env python
"""
Center Deep API Server
A clean API interface for SearXNG with additional features
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
SEARXNG_URL = os.environ.get('SEARXNG_URL', 'http://127.0.0.1:8080')
SEARXNG_TIMEOUT = 10

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """Main search endpoint - proxies to SearXNG and adds Center Deep features"""
    if request.method == 'POST':
        data = request.json
        query = data.get('q', '')
        options = data.get('options', {})
    else:
        query = request.args.get('q', '')
        options = {
            'page': request.args.get('page', 1),
            'categories': request.args.get('categories', ''),
            'time_range': request.args.get('time_range', ''),
            'language': request.args.get('language', 'en'),
            'safesearch': request.args.get('safesearch', '0')
        }
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Build SearXNG request
    params = {
        'q': query,
        'format': 'json',
        'pageno': options.get('page', 1),
        'safesearch': options.get('safesearch', '0'),
        'language': options.get('language', 'en')
    }
    
    if options.get('categories'):
        params['categories'] = options['categories']
    if options.get('time_range'):
        params['time_range'] = options['time_range']
    
    try:
        # Call SearXNG
        response = requests.get(f'{SEARXNG_URL}/search', params=params, timeout=SEARXNG_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Add Center Deep enhancements
            enhanced_results = {
                'query': query,
                'results': data.get('results', []),
                'suggestions': data.get('suggestions', []),
                'answers': data.get('answers', []),
                'infoboxes': data.get('infoboxes', []),
                'number_of_results': len(data.get('results', [])),
                'response_time': data.get('response_time', 0),
                'timestamp': datetime.utcnow().isoformat(),
                'center_deep_version': '2.0.0',
                'powered_by': 'Center Deep + SearXNG'
            }
            
            return jsonify(enhanced_results)
        else:
            return jsonify({'error': 'Search backend error'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Search timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/engines', methods=['GET'])
def get_engines():
    """Get list of available search engines"""
    try:
        response = requests.get(f'{SEARXNG_URL}/config', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'engines': data.get('engines', []),
                'categories': data.get('categories', [])
            })
    except:
        pass
    
    # Fallback response
    return jsonify({
        'engines': ['google', 'bing', 'duckduckgo', 'brave', 'qwant'],
        'categories': ['general', 'images', 'news', 'map', 'music', 'it', 'science', 'files', 'social media']
    })

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get search suggestions"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        response = requests.get(f'{SEARXNG_URL}/autocompleter', 
                              params={'q': query}, 
                              timeout=3)
        if response.status_code == 200:
            return jsonify(response.json())
    except:
        pass
    
    return jsonify([])

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    searxng_healthy = False
    try:
        response = requests.get(f'{SEARXNG_URL}/healthz', timeout=2)
        searxng_healthy = response.status_code == 200
    except:
        pass
    
    return jsonify({
        'status': 'healthy' if searxng_healthy else 'degraded',
        'center_deep': True,
        'searxng': searxng_healthy,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """Serve the React frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api', methods=['GET'])
def api_info():
    """API documentation"""
    return jsonify({
        'name': 'Center Deep API',
        'version': '2.0.0',
        'endpoints': {
            '/api/search': 'Search endpoint (GET/POST)',
            '/api/engines': 'List available search engines',
            '/api/suggestions': 'Get search suggestions',
            '/api/health': 'Health check'
        },
        'description': 'Beautiful search API powered by SearXNG with 250+ search engines',
        'documentation': 'https://github.com/Unicorn-Commander/Center-Deep'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False)
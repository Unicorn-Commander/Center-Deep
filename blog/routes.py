"""
Blog Routes and API Endpoints
Handles blog display, management, and API operations
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
from sqlalchemy import or_, and_, desc
import markdown
import re
from functools import wraps

from app import db, admin_required
from .models import BlogSettings, BlogCategory, BlogPost, BlogComment, AgentTrigger
from agents.models import ContentAgent

# Create blog blueprint
blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

def blog_enabled_required(f):
    """Decorator to check if blog is enabled"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        settings = BlogSettings.query.first()
        if not settings or not settings.blog_enabled:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

# Public blog routes
@blog_bp.route('/')
@blog_enabled_required
def index():
    """Blog landing page"""
    settings = BlogSettings.query.first()
    if not settings:
        # Create default settings
        settings = BlogSettings()
        db.session.add(settings)
        db.session.commit()
    
    page = request.args.get('page', 1, type=int)
    per_page = settings.posts_per_page
    
    # Get published posts
    posts_query = BlogPost.query.filter(
        BlogPost.status == 'published',
        BlogPost.published_at <= datetime.now(timezone.utc)
    ).order_by(desc(BlogPost.published_at))
    
    posts = posts_query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Get featured posts
    featured_posts = []
    if settings.featured_post_ids:
        featured_posts = BlogPost.query.filter(
            BlogPost.id.in_(settings.featured_post_ids),
            BlogPost.status == 'published'
        ).all()
    
    # Get categories for navigation
    categories = BlogCategory.query.filter_by(enabled=True).order_by(BlogCategory.sort_order).all()
    
    return render_template('blog/index.html',
                         settings=settings,
                         posts=posts,
                         featured_posts=featured_posts,
                         categories=categories)

@blog_bp.route('/category/<slug>')
@blog_enabled_required
def category(slug):
    """View posts by category"""
    category = BlogCategory.query.filter_by(slug=slug, enabled=True).first_or_404()
    
    page = request.args.get('page', 1, type=int)
    settings = BlogSettings.query.first()
    per_page = settings.posts_per_page if settings else 10
    
    posts = BlogPost.query.filter(
        BlogPost.category_id == category.id,
        BlogPost.status == 'published',
        BlogPost.published_at <= datetime.now(timezone.utc)
    ).order_by(desc(BlogPost.published_at)).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    categories = BlogCategory.query.filter_by(enabled=True).order_by(BlogCategory.sort_order).all()
    
    return render_template('blog/category.html',
                         category=category,
                         posts=posts,
                         categories=categories,
                         settings=BlogSettings.query.first())

@blog_bp.route('/<slug>')
@blog_enabled_required
def post(slug):
    """View individual blog post"""
    post = BlogPost.query.filter_by(
        slug=slug,
        status='published'
    ).first_or_404()
    
    # Check if post is published
    if post.published_at > datetime.now(timezone.utc):
        abort(404)
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    # Convert markdown to HTML if needed
    content_html = post.content
    if post.content_format == 'markdown':
        content_html = markdown.markdown(post.content, extensions=['codehilite', 'fenced_code'])
    
    # Get related posts
    related_posts = BlogPost.query.filter(
        BlogPost.id != post.id,
        BlogPost.category_id == post.category_id,
        BlogPost.status == 'published'
    ).limit(3).all()
    
    # Get approved comments
    comments = BlogComment.query.filter(
        BlogComment.post_id == post.id,
        BlogComment.status == 'approved',
        BlogComment.parent_id.is_(None)  # Top-level comments only
    ).order_by(BlogComment.created_at).all()
    
    categories = BlogCategory.query.filter_by(enabled=True).order_by(BlogCategory.sort_order).all()
    settings = BlogSettings.query.first()
    
    return render_template('blog/post.html',
                         post=post,
                         content_html=content_html,
                         related_posts=related_posts,
                         comments=comments,
                         categories=categories,
                         settings=settings)

# Admin blog management routes
@blog_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Blog admin dashboard"""
    # Get blog statistics
    stats = {
        'total_posts': BlogPost.query.count(),
        'published_posts': BlogPost.query.filter_by(status='published').count(),
        'draft_posts': BlogPost.query.filter_by(status='draft').count(),
        'pending_posts': BlogPost.query.filter_by(status='pending').count(),
        'total_categories': BlogCategory.query.count(),
        'total_comments': BlogComment.query.count(),
        'pending_comments': BlogComment.query.filter_by(status='pending').count()
    }
    
    # Get recent posts
    recent_posts = BlogPost.query.order_by(desc(BlogPost.updated_at)).limit(10).all()
    
    # Get recent comments
    recent_comments = BlogComment.query.filter_by(status='pending').order_by(
        desc(BlogComment.created_at)
    ).limit(5).all()
    
    settings = BlogSettings.query.first()
    
    return render_template('blog/admin/dashboard.html',
                         stats=stats,
                         recent_posts=recent_posts,
                         recent_comments=recent_comments,
                         settings=settings)

@blog_bp.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    """Blog settings management"""
    settings = BlogSettings.query.first()
    if not settings:
        settings = BlogSettings()
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        
        # Update settings
        for field in ['blog_enabled', 'blog_title', 'blog_subtitle', 'blog_description',
                     'hero_content', 'about_section', 'meta_description', 'meta_keywords',
                     'posts_per_page', 'show_author', 'show_date', 'show_tags',
                     'show_categories', 'enable_social_sharing', 'social_image_url']:
            if field in data:
                if field in ['blog_enabled', 'show_author', 'show_date', 'show_tags',
                           'show_categories', 'enable_social_sharing']:
                    setattr(settings, field, bool(data[field]))
                elif field == 'posts_per_page':
                    setattr(settings, field, int(data[field]))
                else:
                    setattr(settings, field, data[field])
        
        # Handle featured posts
        if 'featured_post_ids' in data:
            featured_ids = data['featured_post_ids']
            if isinstance(featured_ids, str):
                featured_ids = [int(x.strip()) for x in featured_ids.split(',') if x.strip().isdigit()]
            settings.featured_post_ids = featured_ids
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'message': 'Settings updated successfully'})
        else:
            flash('Settings updated successfully', 'success')
            return redirect(url_for('blog.admin_settings'))
    
    if request.is_json:
        return jsonify({
            'blog_enabled': settings.blog_enabled,
            'blog_title': settings.blog_title,
            'blog_subtitle': settings.blog_subtitle,
            'blog_description': settings.blog_description,
            'hero_content': settings.hero_content,
            'about_section': settings.about_section,
            'meta_description': settings.meta_description,
            'meta_keywords': settings.meta_keywords,
            'posts_per_page': settings.posts_per_page,
            'show_author': settings.show_author,
            'show_date': settings.show_date,
            'show_tags': settings.show_tags,
            'show_categories': settings.show_categories,
            'enable_social_sharing': settings.enable_social_sharing,
            'social_image_url': settings.social_image_url,
            'featured_post_ids': settings.featured_post_ids or []
        })
    
    return render_template('blog/admin/settings.html', settings=settings)

# API endpoints for blog management
@blog_bp.route('/api/posts', methods=['GET'])
@login_required
@admin_required
def api_get_posts():
    """Get posts for admin management"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    
    query = BlogPost.query
    
    # Apply filters
    if status:
        query = query.filter(BlogPost.status == status)
    if category_id:
        query = query.filter(BlogPost.category_id == category_id)
    if search:
        query = query.filter(or_(
            BlogPost.title.contains(search),
            BlogPost.content.contains(search)
        ))
    
    posts = query.order_by(desc(BlogPost.updated_at)).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'posts': [{
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'status': post.status,
            'category': post.category.name if post.category else None,
            'author': post.author.username if post.author else 'System',
            'agent': post.agent.name if post.agent else None,
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
            'view_count': post.view_count,
            'word_count': post.word_count,
            'reading_time': post.reading_time
        } for post in posts.items],
        'pagination': {
            'page': posts.page,
            'pages': posts.pages,
            'per_page': posts.per_page,
            'total': posts.total,
            'has_next': posts.has_next,
            'has_prev': posts.has_prev
        }
    })

@blog_bp.route('/api/posts/<int:post_id>', methods=['GET'])
@login_required
@admin_required
def api_get_post(post_id):
    """Get specific post for editing"""
    post = BlogPost.query.get_or_404(post_id)
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'excerpt': post.excerpt,
        'content': post.content,
        'content_format': post.content_format,
        'status': post.status,
        'visibility': post.visibility,
        'category_id': post.category_id,
        'meta_title': post.meta_title,
        'meta_description': post.meta_description,
        'meta_keywords': post.meta_keywords,
        'featured_image_url': post.featured_image_url,
        'tags': post.tags or [],
        'published_at': post.published_at.isoformat() if post.published_at else None,
        'scheduled_for': post.scheduled_for.isoformat() if post.scheduled_for else None,
        'source_data_ids': post.source_data_ids or [],
        'generation_prompt': post.generation_prompt,
        'approval_notes': post.approval_notes
    })

@blog_bp.route('/api/posts', methods=['POST'])
@login_required
@admin_required
def api_create_post():
    """Create new blog post"""
    data = request.get_json()
    
    post = BlogPost(
        title=data['title'],
        content=data['content'],
        excerpt=data.get('excerpt', ''),
        content_format=data.get('content_format', 'markdown'),
        status=data.get('status', 'draft'),
        visibility=data.get('visibility', 'public'),
        category_id=data.get('category_id'),
        author_id=current_user.id,
        meta_title=data.get('meta_title', ''),
        meta_description=data.get('meta_description', ''),
        meta_keywords=data.get('meta_keywords', ''),
        featured_image_url=data.get('featured_image_url', ''),
        tags=data.get('tags', [])
    )
    
    # Handle publishing
    if data.get('status') == 'published' and not post.published_at:
        post.published_at = datetime.now(timezone.utc)
    
    # Handle scheduling
    if data.get('scheduled_for'):
        post.scheduled_for = datetime.fromisoformat(data['scheduled_for'])
        if post.status != 'published':
            post.status = 'scheduled'
    
    post.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Post created successfully',
        'post_id': post.id,
        'slug': post.slug
    })

@blog_bp.route('/api/posts/<int:post_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_post(post_id):
    """Update blog post"""
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json()
    
    # Update fields
    for field in ['title', 'content', 'excerpt', 'content_format', 'status',
                  'visibility', 'category_id', 'meta_title', 'meta_description',
                  'meta_keywords', 'featured_image_url', 'tags', 'approval_notes']:
        if field in data:
            setattr(post, field, data[field])
    
    # Handle publishing
    if data.get('status') == 'published' and not post.published_at:
        post.published_at = datetime.now(timezone.utc)
        post.approved_by = current_user.id
        post.approved_at = datetime.now(timezone.utc)
    
    # Handle scheduling
    if data.get('scheduled_for'):
        post.scheduled_for = datetime.fromisoformat(data['scheduled_for'])
        if post.status != 'published':
            post.status = 'scheduled'
    
    post.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Post updated successfully'
    })

@blog_bp.route('/api/posts/<int:post_id>/status', methods=['PUT'])
@login_required
@admin_required
def api_update_post_status(post_id):
    """Update post status"""
    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json()
    
    new_status = data.get('status')
    if new_status not in ['draft', 'pending', 'published', 'archived']:
        return jsonify({'error': 'Invalid status'}), 400
    
    post.status = new_status
    
    if new_status == 'published' and not post.published_at:
        post.published_at = datetime.now(timezone.utc)
        post.approved_by = current_user.id
        post.approved_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Post status updated to {new_status}'
    })

@blog_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_post(post_id):
    """Delete blog post"""
    post = BlogPost.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Post deleted successfully'
    })

# Categories API
@blog_bp.route('/api/categories', methods=['GET'])
@login_required
@admin_required
def api_get_categories():
    """Get all categories"""
    categories = BlogCategory.query.order_by(BlogCategory.sort_order).all()
    
    return jsonify([{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description,
        'color': cat.color,
        'enabled': cat.enabled,
        'sort_order': cat.sort_order,
        'post_count': len(cat.posts),
        'assigned_agents': cat.assigned_agents or []
    } for cat in categories])

@blog_bp.route('/api/categories', methods=['POST'])
@login_required
@admin_required
def api_create_category():
    """Create new category"""
    data = request.get_json()
    
    category = BlogCategory(
        name=data['name'],
        description=data.get('description', ''),
        color=data.get('color', '#3B82F6'),
        enabled=data.get('enabled', True),
        sort_order=data.get('sort_order', 0),
        assigned_agents=data.get('assigned_agents', [])
    )
    
    category.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Category created successfully',
        'category_id': category.id
    })

@blog_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_category(category_id):
    """Update category"""
    category = BlogCategory.query.get_or_404(category_id)
    data = request.get_json()
    
    for field in ['name', 'description', 'color', 'enabled', 'sort_order', 'assigned_agents']:
        if field in data:
            setattr(category, field, data[field])
    
    category.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Category updated successfully'
    })

# Comment management API
@blog_bp.route('/api/comments', methods=['GET'])
@login_required
@admin_required
def api_get_comments():
    """Get comments for moderation"""
    status = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)
    
    comments = BlogComment.query.filter_by(status=status).order_by(
        desc(BlogComment.created_at)
    ).paginate(page=page, per_page=20, error_out=False)
    
    return jsonify({
        'comments': [{
            'id': comment.id,
            'post_title': comment.post.title,
            'post_slug': comment.post.slug,
            'author_name': comment.author_name,
            'author_email': comment.author_email,
            'content': comment.content,
            'status': comment.status,
            'created_at': comment.created_at.isoformat()
        } for comment in comments.items],
        'pagination': {
            'page': comments.page,
            'pages': comments.pages,
            'total': comments.total
        }
    })

@blog_bp.route('/api/comments/<int:comment_id>/status', methods=['PUT'])
@login_required
@admin_required
def api_update_comment_status(comment_id):
    """Update comment status"""
    comment = BlogComment.query.get_or_404(comment_id)
    data = request.get_json()
    
    new_status = data.get('status')
    if new_status not in ['pending', 'approved', 'spam', 'deleted']:
        return jsonify({'error': 'Invalid status'}), 400
    
    comment.status = new_status
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Comment status updated to {new_status}'
    })

# Register the blueprint
def register_blog_routes(app):
    """Register blog routes with the Flask app"""
    app.register_blueprint(blog_bp)
    
    # Add blog context to all templates
    @app.context_processor
    def inject_blog_settings():
        settings = BlogSettings.query.first()
        return dict(blog_settings=settings)
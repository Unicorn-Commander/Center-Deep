# Center Deep Extensions for SearXNG
__version__ = "1.0.0"

from .auth import init_auth
from .admin import init_admin
from .models import init_db

def init_center_deep(app):
    """Initialize Center Deep extensions"""
    init_db(app)
    init_auth(app)
    init_admin(app)
    return app
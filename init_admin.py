#!/usr/bin/env python3
"""Initialize or update admin credentials for Center Deep"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def init_admin():
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check for existing admin
        admin = User.query.filter_by(username='ucadmin').first()
        
        if admin:
            print("✅ Admin user 'ucadmin' already exists")
            if not admin.password_changed:
                print("⚠️  Using default password. Please change it after login!")
                print("   Default credentials: ucadmin / MagicUnicorn!8-)")
        else:
            # Remove old admin if exists
            old_admin = User.query.filter_by(username='admin').first()
            if old_admin:
                db.session.delete(old_admin)
                print("🗑️  Removed old 'admin' user")
            
            # Create new admin with proper credentials
            admin = User(
                username='ucadmin',
                email='admin@center-deep.com',
                is_admin=True,
                password_changed=False  # Mark as default password
            )
            admin.set_password('MagicUnicorn!8-)')
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Created admin user 'ucadmin'")
            print("📝 Default credentials: ucadmin / MagicUnicorn!8-)")
            print("⚠️  Please change the password after first login!")
        
        # Show all users
        print("\n📊 Current users in database:")
        users = User.query.all()
        for user in users:
            status = "Admin" if user.is_admin else "User"
            pwd_status = "Custom" if user.password_changed else "Default"
            print(f"   - {user.username} ({status}) - Password: {pwd_status}")

if __name__ == '__main__':
    init_admin()
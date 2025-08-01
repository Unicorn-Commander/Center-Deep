#!/usr/bin/env python3
"""Update admin user credentials"""

import os
import sys
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "instance", "center_deep.db")
database_uri = f'sqlite:///{db_path}'

def update_admin_credentials():
    """Update admin user credentials"""
    try:
        engine = create_engine(database_uri)
        
        # New credentials
        new_username = 'ucadmin'
        new_password = 'MagicUnicorn!8-)'
        password_hash = generate_password_hash(new_password)
        
        with engine.connect() as conn:
            # Check if admin exists
            result = conn.execute(text("SELECT id FROM user WHERE username = 'admin'"))
            admin_user = result.fetchone()
            
            if admin_user:
                # Update existing admin
                conn.execute(
                    text("UPDATE user SET username = :username, password_hash = :password WHERE id = :id"),
                    {"username": new_username, "password": password_hash, "id": admin_user[0]}
                )
                print(f"Updated admin user credentials:")
            else:
                # Create new admin
                conn.execute(
                    text("""
                        INSERT INTO user (username, email, password_hash, is_admin, created_at) 
                        VALUES (:username, :email, :password, :is_admin, datetime('now'))
                    """),
                    {
                        "username": new_username, 
                        "email": "admin@centerdeep.com",
                        "password": password_hash,
                        "is_admin": True
                    }
                )
                print(f"Created admin user:")
            
            conn.commit()
            
        print(f"  Username: {new_username}")
        print(f"  Password: {new_password}")
        print("\nAdmin credentials updated successfully!")
        
    except Exception as e:
        print(f"Error updating admin credentials: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_admin_credentials()
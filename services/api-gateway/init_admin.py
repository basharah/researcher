"""
Initialize database with default admin user
Run this after database migrations
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models import User, UserRole
from passlib.context import CryptContext
import uuid
from datetime import datetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_default_admin():
    """Create default admin user if not exists"""
    db = SessionLocal()
    
    try:
        # Default admin credentials
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@bashars.eu")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
        admin_name = os.getenv("DEFAULT_ADMIN_NAME", "System Administrator")
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if existing_admin:
            print(f"✓ Admin user already exists: {admin_email}")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            user_id=str(uuid.uuid4()),
            email=admin_email,
            password_hash=pwd_context.hash(admin_password),
            full_name=admin_name,
            organization="System",
            role=UserRole.ADMIN,
            disabled=False,
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✓ Created default admin user:")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
        print(f"  Role: {admin_user.role.value}")
        print(f"  User ID: {admin_user.user_id}")
        print(f"\n⚠️  IMPORTANT: Change the default password after first login!")
        
        return admin_user
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database with default admin user...")
    print("-" * 50)
    create_default_admin()
    print("-" * 50)
    print("✓ Initialization complete!")

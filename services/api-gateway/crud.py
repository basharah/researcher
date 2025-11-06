"""
User CRUD Operations
Database operations for user management with PostgreSQL
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from models import User, APIKey, RefreshToken, UserRole
from auth_schemas import UserRegister

logger = logging.getLogger(__name__)


class UserCRUD:
    """User database operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserRegister, password_hash: str) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: User registration data
            password_hash: Hashed password (from bcrypt)
            
        Returns:
            Created User object
            
        Raises:
            IntegrityError: If email already exists
        """
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        
        db_user = User(
            user_id=user_id,
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
            organization=user_data.organization,
            role=UserRole.USER,
            disabled=False,
            email_verified=False
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User created: {user_data.email} ({user_id})")
            return db_user
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Failed to create user {user_data.email}: {e}")
            raise ValueError("Email already registered")
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email address"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users (paginated)"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user fields
        
        Args:
            db: Database session
            user_id: User ID to update
            **kwargs: Fields to update (full_name, organization, etc.)
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.email}")
        return user
    
    @staticmethod
    def update_last_login(db: Session, user_id: str):
        """Update user's last login timestamp"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def disable_user(db: Session, user_id: str) -> bool:
        """Disable a user account"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        user.disabled = True
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"User disabled: {user.email}")
        return True
    
    @staticmethod
    def enable_user(db: Session, user_id: str) -> bool:
        """Enable a user account"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        user.disabled = False
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"User enabled: {user.email}")
        return True
    
    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """
        Permanently delete a user
        
        WARNING: This is irreversible! Consider disabling instead.
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        
        logger.warning(f"User deleted permanently: {user.email}")
        return True
    
    @staticmethod
    def change_password(db: Session, user_id: str, new_password_hash: str) -> bool:
        """Change user password"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        
        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        return True


class APIKeyCRUD:
    """API Key database operations"""
    
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: str,
        api_key: str,
        name: str,
        expires_at: Optional[datetime] = None
    ) -> APIKey:
        """Create a new API key"""
        db_key = APIKey(
            api_key=api_key,
            user_id=user_id,
            name=name,
            expires_at=expires_at,
            disabled=False
        )
        
        db.add(db_key)
        db.commit()
        db.refresh(db_key)
        
        logger.info(f"API key created: {name} for user {user_id}")
        return db_key
    
    @staticmethod
    def get_api_key(db: Session, api_key: str) -> Optional[APIKey]:
        """Get API key by key value"""
        return db.query(APIKey).filter(APIKey.api_key == api_key).first()
    
    @staticmethod
    def get_user_api_keys(db: Session, user_id: str) -> List[APIKey]:
        """Get all API keys for a user"""
        return db.query(APIKey).filter(APIKey.user_id == user_id).all()
    
    @staticmethod
    def revoke_api_key(db: Session, api_key: str) -> bool:
        """Revoke an API key (soft delete)"""
        key = db.query(APIKey).filter(APIKey.api_key == api_key).first()
        if not key:
            return False
        
        key.disabled = True
        db.commit()
        
        logger.info(f"API key revoked: {key.name}")
        return True
    
    @staticmethod
    def update_last_used(db: Session, api_key: str):
        """Update API key last used timestamp"""
        key = db.query(APIKey).filter(APIKey.api_key == api_key).first()
        if key:
            key.last_used = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def delete_api_key(db: Session, api_key: str) -> bool:
        """Permanently delete an API key"""
        key = db.query(APIKey).filter(APIKey.api_key == api_key).first()
        if not key:
            return False
        
        db.delete(key)
        db.commit()
        
        logger.info(f"API key deleted: {key.name}")
        return True


class RefreshTokenCRUD:
    """Refresh token database operations"""
    
    @staticmethod
    def store_refresh_token(
        db: Session,
        token_hash: str,
        user_id: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RefreshToken:
        """Store a refresh token"""
        db_token = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            revoked=False
        )
        
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        
        return db_token
    
    @staticmethod
    def get_refresh_token(db: Session, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash"""
        return db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
    
    @staticmethod
    def revoke_refresh_token(db: Session, token_hash: str) -> bool:
        """Revoke a refresh token"""
        token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if not token:
            return False
        
        token.revoked = True
        db.commit()
        return True
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: str) -> int:
        """Revoke all refresh tokens for a user (logout all sessions)"""
        count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).update({"revoked": True})
        
        db.commit()
        logger.info(f"Revoked {count} refresh tokens for user {user_id}")
        return count
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Delete expired refresh tokens (maintenance task)"""
        count = db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {count} expired refresh tokens")
        return count

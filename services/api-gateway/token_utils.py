"""
Token Utilities
Helper functions for token management
"""
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from crud import RefreshTokenCRUD
from config import settings


def hash_token(token: str) -> str:
    """Hash a token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def store_refresh_token_db(db: Session, token: str, user_id: str):
    """
    Store a refresh token in the database
    
    Args:
        db: Database session
        token: The actual refresh token (will be hashed)
        user_id: User ID who owns the token
    """
    token_hash = hash_token(token)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    return RefreshTokenCRUD.store_refresh_token(
        db=db,
        token_hash=token_hash,
        user_id=user_id,
        expires_at=expires_at
    )


def verify_refresh_token_db(db: Session, token: str) -> bool:
    """
    Verify a refresh token exists in database and is not revoked
    
    Args:
        db: Database session
        token: The refresh token to verify
        
    Returns:
        True if token is valid, False otherwise
    """
    token_hash = hash_token(token)
    token_record = RefreshTokenCRUD.get_refresh_token(db, token_hash)
    
    if not token_record:
        return False
    
    if token_record.revoked:
        return False
    
    if token_record.expires_at < datetime.utcnow():
        return False
    
    return True


def revoke_refresh_token_db(db: Session, token: str) -> bool:
    """
    Revoke a refresh token
    
    Args:
        db: Database session
        token: The refresh token to revoke
        
    Returns:
        True if successfully revoked
    """
    token_hash = hash_token(token)
    return RefreshTokenCRUD.revoke_refresh_token(db, token_hash)

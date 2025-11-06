"""
User Models for PostgreSQL
SQLAlchemy models for persistent user storage
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    RESEARCHER = "researcher"  # Optional: special role for researchers


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(100), nullable=False)
    organization = Column(String(100), nullable=True)
    
    # Authorization
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Status
    disabled = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "full_name": self.full_name,
            "organization": self.organization,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "created_at": self.created_at.isoformat(),
            "disabled": self.disabled,
            "email_verified": self.email_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class APIKey(Base):
    """API Key model for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)  # FK to users.user_id
    
    name = Column(String(100), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # NULL = never expires
    last_used = Column(DateTime, nullable=True)
    
    disabled = Column(Boolean, default=False, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "api_key": self.api_key,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "disabled": self.disabled
        }


class RefreshToken(Base):
    """Refresh token storage for JWT token rotation"""
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA256 hash
    user_id = Column(String(50), nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    revoked = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length

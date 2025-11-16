"""
Authentication Schemas
Pydantic models for authentication requests and responses
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User information response"""
    user_id: str
    email: str
    full_name: str
    organization: Optional[str]
    role: str
    created_at: datetime
    disabled: bool = False


class UserUpdate(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class AdminUserCreate(BaseModel):
    """Admin create user request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field("user", description="User role: user or admin")
    disabled: Optional[bool] = False
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class AdminUserUpdate(BaseModel):
    """Admin update user request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, description="User role: user or admin")
    disabled: Optional[bool] = None


class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=1, max_length=100, description="Name to identify this API key")
    expires_in_days: Optional[int] = Field(None, gt=0, le=365, description="Days until key expires (optional, max 365)")


class APIKeyResponse(BaseModel):
    """API key response"""
    api_key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "rpa_abc123...",
                "name": "My Research App",
                "created_at": "2025-01-06T12:00:00Z",
                "expires_at": "2025-02-05T12:00:00Z"
            }
        }


class LogoutRequest(BaseModel):
    """Logout request (optional, can also use from token)"""
    revoke_all: bool = False  # Revoke all sessions/tokens

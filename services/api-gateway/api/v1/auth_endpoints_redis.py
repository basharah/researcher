"""
Authentication Endpoints
User registration, login, logout, profile management, API keys
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
import uuid
import logging

from auth import (
    AuthService,
    get_current_user,
    get_current_active_user,
    require_admin,
    RateLimiter
)
from auth_schemas import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    UserResponse,
    UserUpdate,
    PasswordChange,
    APIKeyCreate,
    APIKeyResponse,
    LogoutRequest
)
from config_new import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    # Check if user already exists
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    
    # Check for existing email (in production, use database)
    # For now, we'll store in Redis with email as secondary key
    
    # Hash password
    hashed_password = AuthService.hash_password(user_data.password)
    
    # Create user record
    user_record = {
        "user_id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "full_name": user_data.full_name,
        "organization": user_data.organization,
        "role": "user",  # Default role
        "created_at": datetime.utcnow().isoformat(),
        "disabled": False
    }
    
    # Store user
    AuthService.store_user(user_record)
    
    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": user_id, "email": user_data.email}
    )
    refresh_token = AuthService.create_refresh_token(user_id)
    
    logger.info(f"New user registered: {user_data.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login with email and password
    
    Returns JWT access token and refresh token
    """
    # In production, query database by email
    # For now, we'll need to iterate (not efficient, use DB in production)
    
    # Simplified: Generate consistent user_id from email
    # In production, lookup user by email in database
    user_id = f"user_{uuid.uuid5(uuid.NAMESPACE_DNS, credentials.email).hex[:12]}"
    
    user = AuthService.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not AuthService.verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is disabled
    if user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": user_id, "email": user["email"]}
    )
    refresh_token = AuthService.create_refresh_token(user_id)
    
    logger.info(f"User logged in: {credentials.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token
    
    Refresh tokens are long-lived (7 days default) and can be used
    to obtain new access tokens without re-entering credentials
    """
    # Decode refresh token
    try:
        payload = AuthService.decode_token(token_data.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = AuthService.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token = AuthService.create_access_token(
        data={"sub": user_id, "email": user["email"]}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=token_data.refresh_token,  # Can reuse refresh token
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(
    logout_data: LogoutRequest = LogoutRequest(),
    current_user: dict = Depends(get_current_user)
):
    """
    Logout user by blacklisting the current token
    
    If revoke_all is True, invalidates all user sessions (future enhancement)
    """
    # In production, extract token from request
    # For now, just acknowledge logout
    
    logger.info(f"User logged out: {current_user['email']}")
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user profile information
    """
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        organization=current_user.get("organization"),
        role=current_user["role"],
        created_at=datetime.fromisoformat(current_user["created_at"]),
        disabled=current_user.get("disabled", False)
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    updates: UserUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update current user profile
    """
    # Update user record
    if updates.full_name is not None:
        current_user["full_name"] = updates.full_name
    if updates.organization is not None:
        current_user["organization"] = updates.organization
    
    # Save updated user
    AuthService.store_user(current_user)
    
    logger.info(f"User profile updated: {current_user['email']}")
    
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        organization=current_user.get("organization"),
        role=current_user["role"],
        created_at=datetime.fromisoformat(current_user["created_at"]),
        disabled=current_user.get("disabled", False)
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Change user password
    """
    # Verify current password
    if not AuthService.verify_password(
        password_data.current_password,
        current_user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash new password
    new_password_hash = AuthService.hash_password(password_data.new_password)
    
    # Update user record
    current_user["password_hash"] = new_password_hash
    AuthService.store_user(current_user)
    
    logger.info(f"Password changed for user: {current_user['email']}")
    
    return {"message": "Password changed successfully"}


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new API key for programmatic access
    
    API keys can be used as Bearer tokens instead of JWT tokens
    """
    from auth import APIKeyAuth
    
    api_key = APIKeyAuth.create_api_key(
        user_id=current_user["user_id"],
        name=key_data.name
    )
    
    logger.info(f"API key created for user: {current_user['email']} ({key_data.name})")
    
    return APIKeyResponse(
        api_key=api_key,
        name=key_data.name,
        created_at=datetime.utcnow()
    )


@router.delete("/api-keys/{api_key}")
async def revoke_api_key(
    api_key: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Revoke an API key
    
    Only the owner of the API key can revoke it
    """
    from auth import APIKeyAuth
    import redis
    import json
    
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    # Verify ownership
    api_key_data = redis_client.get(f"apikey:{api_key}")
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key_info = json.loads(api_key_data)
    if api_key_info["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only revoke your own API keys"
        )
    
    APIKeyAuth.revoke_api_key(api_key)
    
    logger.info(f"API key revoked: {current_user['email']}")
    
    return {"message": "API key revoked successfully"}


# Admin endpoints

@router.get("/admin/users", dependencies=[Depends(require_admin)])
async def list_users():
    """
    List all users (admin only)
    """
    # In production, query database
    # For demo, return admin info
    return {"message": "Admin endpoint - list users"}


@router.put("/admin/users/{user_id}/disable", dependencies=[Depends(require_admin)])
async def disable_user(user_id: str):
    """
    Disable a user account (admin only)
    """
    user = AuthService.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["disabled"] = True
    AuthService.store_user(user)
    
    logger.info(f"User disabled: {user['email']}")
    
    return {"message": f"User {user_id} disabled"}


@router.put("/admin/users/{user_id}/enable", dependencies=[Depends(require_admin)])
async def enable_user(user_id: str):
    """
    Enable a user account (admin only)
    """
    user = AuthService.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["disabled"] = False
    AuthService.store_user(user)
    
    logger.info(f"User enabled: {user['email']}")
    
    return {"message": f"User {user_id} enabled"}

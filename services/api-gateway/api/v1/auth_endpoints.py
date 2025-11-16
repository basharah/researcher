"""
Authentication Endpoints - PostgreSQL Version
User registration, login, logout, profile management, API keys
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import logging

from auth import (
    AuthService,
    get_current_user,
    get_current_active_user,
    require_admin
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
    LogoutRequest,
    AdminUserCreate,
    AdminUserUpdate,
)
from database import get_db
from crud import UserCRUD, APIKeyCRUD
from token_utils import (
    store_refresh_token_db,
    verify_refresh_token_db,
    revoke_refresh_token_db
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    # Check if user already exists
    existing_user = UserCRUD.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = AuthService.hash_password(user_data.password)
    
    # Create user
    user = UserCRUD.create_user(
        db=db,
        user_data=user_data,
        password_hash=password_hash
    )
    
    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": user.user_id, "email": user.email, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)}
    )
    
    # Create and store refresh token
    refresh_token = AuthService.create_refresh_token(user.user_id)
    store_refresh_token_db(db, refresh_token, user.user_id)
    
    logger.info(f"New user registered: {user.email} (from {request.client.host})")
    
    from config import settings

    # Set HttpOnly cookies for access and refresh tokens
    access_max_age = settings.access_token_expire_minutes * 60
    refresh_max_age = settings.refresh_token_expire_days * 24 * 3600

    secure = not settings.debug

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=access_max_age,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=refresh_max_age,
        path="/"
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=access_max_age
    )


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    Returns access token and refresh token
    """
    # Log the login attempt (email only)
    logger.info(f"Login attempt for: {credentials.email} from {request.client.host} origin={request.headers.get('origin')}")

    # Get user
    user = UserCRUD.get_user_by_email(db, credentials.email)
    if not user:
        logger.info(f"Login failed: user not found for email={credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not AuthService.verify_password(credentials.password, user.password_hash):
        logger.info(f"Login failed: incorrect password for email={credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is disabled
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    UserCRUD.update_last_login(db, user.user_id)
    
    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": user.user_id, "email": user.email, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)}
    )
    
    # Create and store refresh token
    refresh_token = AuthService.create_refresh_token(user.user_id)
    store_refresh_token_db(db, refresh_token, user.user_id)
    
    logger.info(f"User logged in: {user.email}")
    
    from config import settings

    access_max_age = settings.access_token_expire_minutes * 60
    refresh_max_age = settings.refresh_token_expire_days * 24 * 3600
    secure = not settings.debug

    logger.info(f"Setting cookies: secure={secure}, debug={settings.debug}, access_max_age={access_max_age}, refresh_max_age={refresh_max_age}")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=access_max_age,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=refresh_max_age,
        path="/"
    )
    logger.info(f"Cookies set successfully for user: {user.email}")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=access_max_age
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Get new access token using refresh token
    """
    # Verify refresh token JWT signature
    payload = AuthService.verify_refresh_token(token_data.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload"
        )
    
    # Verify refresh token exists in database and is not revoked
    if not verify_refresh_token_db(db, token_data.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or expired"
        )
    
    # Get user
    user = UserCRUD.get_user_by_id(db, user_id)
    if not user or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled"
        )
    
    # Create new access token
    access_token = AuthService.create_access_token(
        data={"sub": user.user_id, "email": user.email, "role": user.role.value if hasattr(user.role, 'value') else str(user.role)}
    )
    
    from config import settings
    
    return Token(
        access_token=access_token,
        refresh_token=token_data.refresh_token,  # Return same refresh token
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60  # Convert to seconds
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    logout_data: LogoutRequest | None = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user - invalidates access token and optionally refresh token
    """
    # Blacklist access token (from body if provided, otherwise try cookie)
    access_token = None
    refresh_token = None
    if logout_data:
        access_token = getattr(logout_data, "access_token", None)
        refresh_token = getattr(logout_data, "refresh_token", None)

    if not access_token:
        access_token = request.cookies.get("access_token")

    if access_token:
        AuthService.blacklist_token(access_token)

    # Revoke refresh token if provided (body) or from cookie
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        revoke_refresh_token_db(db, refresh_token)
    
    logger.info(f"User logged out: {current_user['email']}")

    # Delete cookies
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile
    Requires valid access token
    """
    user = UserCRUD.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user.to_dict())


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    # Update user
    updated_user = UserCRUD.update_user(
        db=db,
        user_id=current_user["user_id"],
        full_name=update_data.full_name,
        organization=update_data.organization
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User profile updated: {current_user['email']}")
    
    return UserResponse(**updated_user.to_dict())


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user's password
    """
    # Get user
    user = UserCRUD.get_user_by_id(db, current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not AuthService.verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_password_hash = AuthService.hash_password(password_data.new_password)
    
    # Change password
    success = UserCRUD.change_password(
        db=db,
        user_id=user.user_id,
        new_password_hash=new_password_hash
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
    
    logger.info(f"Password changed for user: {current_user['email']}")
    
    return {"message": "Password changed successfully"}


# ==================== API Key Management ====================

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key for automation
    """
    # Generate API key
    api_key = f"rpa_{uuid.uuid4().hex}"
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Store API key
    api_key_record = APIKeyCRUD.create_api_key(
        db=db,
        user_id=current_user["user_id"],
        api_key=api_key,
        name=key_data.name,
        expires_at=expires_at
    )
    
    logger.info(f"API key created for user: {current_user['email']}")
    
    return APIKeyResponse(
        api_key=api_key,
        name=api_key_record.name,
        created_at=api_key_record.created_at,
        expires_at=api_key_record.expires_at
    )


@router.get("/api-keys")
async def list_api_keys(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for current user
    """
    api_keys = APIKeyCRUD.get_user_api_keys(db, current_user["user_id"])
    
    return {
        "api_keys": [
            {
                "key_id": key.id,
                "name": key.name,
                "api_key": key.api_key[:8] + "..." + key.api_key[-4:],  # Masked
                "created_at": key.created_at,
                "expires_at": key.expires_at,
                "last_used": key.last_used
            }
            for key in api_keys
        ]
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key
    """
    # Get all user's API keys
    user_keys = APIKeyCRUD.get_user_api_keys(db, current_user["user_id"])
    
    # Find the key by ID
    api_key_str = None
    for key in user_keys:
        if key.id == key_id:
            api_key_str = key.api_key
            break
    
    if not api_key_str:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Revoke key
    success = APIKeyCRUD.revoke_api_key(db, api_key_str)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke API key"
        )
    
    logger.info(f"API key revoked: {key_id}")
    
    return {"message": "API key revoked successfully"}


# ==================== Admin Endpoints ====================

@router.get("/admin/users")
async def list_all_users(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only)
    """
    users = UserCRUD.get_all_users(db)
    
    return {
        "users": [
            {
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": getattr(user.role, "value", user.role),
                "disabled": user.disabled,
                "created_at": user.created_at
            }
            for user in users
        ]
    }


@router.post("/admin/users", response_model=UserResponse)
async def admin_create_user(
    new_user: AdminUserCreate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only)
    """
    # Hash password
    password_hash = AuthService.hash_password(new_user.password)

    # Create base user as normal
    db_user = UserCRUD.create_user(
        db=db,
        user_data=UserRegister(
            email=new_user.email,
            password=new_user.password,
            full_name=new_user.full_name,
            organization=new_user.organization,
        ),
        password_hash=password_hash,
    )

    # Apply admin-provided role/disabled if specified
    from models import UserRole
    role_value = (new_user.role or "user").lower()
    try:
        role_enum = UserRole(role_value)
    except Exception:
        role_enum = UserRole.USER

    updated = UserCRUD.update_user(
        db=db,
        user_id=db_user.user_id,
        role=role_enum,
        disabled=bool(new_user.disabled),
    )

    return UserResponse(**updated.to_dict())


@router.put("/admin/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: str,
    updates: AdminUserUpdate,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update an existing user (admin only)
    """
    from models import UserRole

    update_fields = {
        "full_name": updates.full_name,
        "organization": updates.organization,
    }

    if updates.role is not None:
        try:
            update_fields["role"] = UserRole(updates.role)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role. Use 'user' or 'admin'.")

    if updates.disabled is not None:
        update_fields["disabled"] = bool(updates.disabled)

    user = UserCRUD.update_user(db, user_id, **update_fields)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**user.to_dict())


@router.put("/admin/users/{user_id}/disable")
async def disable_user(
    user_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Disable a user account (admin only)
    """
    success = UserCRUD.disable_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User disabled by admin: {user_id}")
    
    return {"message": f"User {user_id} disabled successfully"}


@router.put("/admin/users/{user_id}/enable")
async def enable_user(
    user_id: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Enable a user account (admin only)
    """
    success = UserCRUD.enable_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User enabled by admin: {user_id}")
    
    return {"message": f"User {user_id} enabled successfully"}


@router.put("/admin/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    role: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Change a user's role (admin only)
    Valid roles: user, admin
    """
    from models import UserRole
    
    # Validate role
    try:
        role_enum = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}"
        )
    
    user = UserCRUD.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update role
    updated_user = UserCRUD.update_user(db, user_id, role=role_enum)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change user role"
        )
    
    logger.info(f"User role changed by admin: {user_id} -> {role}")
    
    return {"message": f"User {user_id} role changed to {role}"}

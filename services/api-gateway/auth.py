"""
Authentication and Security Module
Provides JWT-based authentication, user management, and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import json
import logging

from config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token bearer - auto_error=False allows it to return None instead of raising
security = HTTPBearer(auto_error=False)

# Redis client for token blacklist and session management
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


class AuthService:
    """Authentication service for user management and JWT tokens"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Payload to encode (should include 'sub' for user identifier)
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create a refresh token for renewing access tokens"""
        return AuthService.create_access_token(
            data={"sub": user_id, "type": "refresh"},
            expires_delta=timedelta(days=settings.refresh_token_expire_days)
        )
    
    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a refresh token
        
        Returns:
            Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                return None
            
            return payload
        except JWTError as e:
            logger.warning(f"Invalid refresh token: {e}")
            return None
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token
        
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Invalid token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """Check if token has been revoked/blacklisted"""
        return redis_client.exists(f"blacklist:{token}") > 0
    
    @staticmethod
    def blacklist_token(token: str, expires_in: int = None):
        """
        Add token to blacklist (for logout)
        
        Args:
            token: JWT token to blacklist
            expires_in: Seconds until automatic removal (default: token expiration)
        """
        if expires_in is None:
            # Extract expiration from token
            try:
                payload = jwt.decode(
                    token,
                    settings.secret_key,
                    algorithms=[settings.jwt_algorithm],
                    options={"verify_exp": False}
                )
                exp = payload.get("exp")
                if exp:
                    expires_in = int(exp - datetime.utcnow().timestamp())
            except:
                expires_in = settings.access_token_expire_minutes * 60
        
        redis_client.setex(
            f"blacklist:{token}",
            expires_in,
            "1"
        )
        logger.info("Token blacklisted")
    
    @staticmethod
    def store_user(user_data: Dict[str, Any]):
        """Store user data in Redis (temporary - replace with DB in production)"""
        user_id = user_data["user_id"]
        redis_client.setex(
            f"user:{user_id}",
            86400 * 30,  # 30 days
            json.dumps(user_data)
        )
    
    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data from Redis"""
        user_data = redis_client.get(f"user:{user_id}")
        if user_data:
            return json.loads(user_data)
        return None
    
    @staticmethod
    def delete_user(user_id: str):
        """Delete user from Redis"""
        redis_client.delete(f"user:{user_id}")


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token
    
    Returns user dict with keys: user_id, email, full_name, organization, role, disabled
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    token = None

    # Prefer Authorization header if present
    if credentials:
        token = credentials.credentials
        logger.info(f"Token from Authorization header: {token[:20]}...")
    else:
        # Fall back to cookie named 'access_token'
        token = request.cookies.get("access_token")
        if token:
            logger.info(f"Token from cookie: {token[:20]}...")
        else:
            logger.info(f"No token in Authorization header or cookies. Available cookies: {list(request.cookies.keys())}")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is blacklisted
    if AuthService.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate token
    payload = AuthService.decode_token(token)
    
    # Check if it's an access token (not refresh)
    if payload.get("type") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return basic user info from token
    # Full user data can be fetched from DB by endpoint if needed
    return {
        "user_id": user_id,
        "email": email
    }


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active user
    Note: Disabled status should be checked in endpoints that need it
    """
    return current_user


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Dependency to require admin role
    
    Usage:
        @router.delete("/admin/users/{user_id}")
        async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
            # Only admins can access this
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


class RateLimiter:
    """Rate limiting for API endpoints"""
    
    @staticmethod
    def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
        """
        Check if rate limit is exceeded
        
        Args:
            key: Identifier (e.g., user_id, IP address)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if within limit, False if exceeded
        """
        current_time = datetime.utcnow().timestamp()
        window_key = f"ratelimit:{key}:{int(current_time / window_seconds)}"
        
        current_count = redis_client.incr(window_key)
        
        if current_count == 1:
            redis_client.expire(window_key, window_seconds)
        
        return current_count <= max_requests
    
    @staticmethod
    async def check_user_rate_limit(
        user: Dict[str, Any] = Depends(get_current_user)
    ):
        """
        Dependency to enforce rate limiting per user
        
        Usage:
            @router.post("/analyze", dependencies=[Depends(RateLimiter.check_user_rate_limit)])
        """
        user_id = user["user_id"]
        
        if not RateLimiter.check_rate_limit(
            f"user:{user_id}",
            settings.rate_limit_requests,
            60  # 1 minute window
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {settings.rate_limit_requests} requests per minute."
            )


# API Key authentication (alternative to JWT for service-to-service)
class APIKeyAuth:
    """API Key authentication for service-to-service communication"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key against stored keys in Redis"""
        return redis_client.exists(f"apikey:{api_key}") > 0
    
    @staticmethod
    def create_api_key(user_id: str, name: str) -> str:
        """Generate a new API key for a user"""
        import secrets
        api_key = f"rpa_{secrets.token_urlsafe(32)}"  # rpa = Research Paper Analysis
        
        api_key_data = {
            "user_id": user_id,
            "name": name,
            "created_at": datetime.utcnow().isoformat()
        }
        
        redis_client.setex(
            f"apikey:{api_key}",
            86400 * 365,  # 1 year
            json.dumps(api_key_data)
        )
        
        return api_key
    
    @staticmethod
    def revoke_api_key(api_key: str):
        """Revoke an API key"""
        redis_client.delete(f"apikey:{api_key}")


async def get_user_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to authenticate using API key
    
    Usage:
        @router.post("/upload", dependencies=[Depends(get_user_from_api_key)])
    """
    api_key = credentials.credentials
    
    if not api_key.startswith("rpa_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key_data = redis_client.get(f"apikey:{api_key}")
    if not api_key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key_info = json.loads(api_key_data)
    user_id = api_key_info["user_id"]
    
    user = AuthService.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

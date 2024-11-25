# Standard library imports
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import logging


# Third-party imports
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

# Local application imports
from ..config import get_settings
from ..dependencies import get_db
from ..models.user import User, UserRole

# Initialize settings and security contexts
settings = get_settings()
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # For password hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # FastAPI's OAuth2 scheme

# Password verification helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a hash from a plain password."""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {email}")
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.
    Args:
        data: Payload to encode in the token
        expires_delta: Optional custom expiration time
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default expiration time from settings if not specified
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency to get the current authenticated user from a JWT token.
    Used to protect endpoints that require authentication.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and validate the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Verify user exists in database
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def get_google_oauth_client():
    """Create and configure Google OAuth client"""
    oauth = OAuth()
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return oauth.google 

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if current user is an admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def check_user_role(user: User, allowed_roles: List[UserRole]) -> bool:
    """Check if user has any of the allowed roles"""
    return user.role in allowed_roles

async def get_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if current user is a super admin"""
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user

async def get_admin_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Check if current user is an admin or super admin"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_creator_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Check if user can create content"""
    if current_user.role not in [
        UserRole.CREATOR,
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.PREMIUM
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creator privileges required"
        )
    return current_user

async def get_premium_user(current_user: User = Depends(get_current_user)) -> User:
    """Check if user has premium access"""
    if current_user.role not in [UserRole.PREMIUM, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    # Check if premium subscription is expired
    if (current_user.role == UserRole.PREMIUM and 
        current_user.subscription_expires and 
        current_user.subscription_expires < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription has expired"
        )
    return current_user

# Add the following import at the top of the file
import logging

# Initialize the logger
logger = logging.getLogger(__name__)
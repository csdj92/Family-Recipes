from fastapi import Request, HTTPException, status
from typing import Optional, Dict
import jwt
import time
from functools import lru_cache
import logging
from uuid import UUID
from enum import Enum
from ..config import get_settings
from ..schemas.user import UserRole  # Import UserRole from schemas

logger = logging.getLogger(__name__)
settings = get_settings()

async def verify_supabase_jwt(request: Request) -> Optional[dict]:
    """Verify Supabase JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        token = auth_header.split(' ')[1]
        
        try:
            # Decode and verify the JWT using the JWT secret
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,  # Use the JWT secret from your Supabase project settings
                algorithms=["HS256"],
                audience="authenticated"
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def get_user_id_from_jwt(token_data: dict) -> UUID:
    """Extract user ID from Supabase JWT claims"""
    if not token_data or 'sub' not in token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    try:
        return UUID(token_data['sub'])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format"
        )

def get_user_role(token_data: dict) -> UserRole:
    """Get user role from JWT claims"""
    role = token_data.get('app_metadata', {}).get('role', UserRole.MEMBER)
    try:
        return UserRole(role)
    except ValueError:
        return UserRole.MEMBER

def require_role(*allowed_roles: UserRole):
    """Decorator to require specific roles for access"""
    async def role_checker(request: Request):
        token_data = request.state.user
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        user_role = get_user_role(token_data)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(r.value for r in allowed_roles)}"
            )
        return token_data
    return role_checker

async def get_current_user(request: Request):
    """Get current authenticated user data"""
    user_data = request.state.user
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user_data 
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PREMIUM = "premium"
    CREATOR = "creator"
    MEMBER = "member"
    GUEST = "guest"

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserProfile(UserBase):
    id: UUID
    role: UserRole
    created_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserProfile):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class TokenData(BaseModel):
    sub: Optional[str] = None  # Supabase uses 'sub' as the user ID
    email: Optional[str] = None
    role: Optional[str] = None
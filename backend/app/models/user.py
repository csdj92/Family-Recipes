from sqlalchemy import Column, String, UUID, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
import uuid
import enum
from sqlalchemy.types import Boolean

from ..models.database import Base

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"      # Can manage all system settings and users
    ADMIN = "admin"                  # Can manage users and content moderation
    PREMIUM = "premium"              # Premium users with extra features
    CREATOR = "creator"              # Can create and share recipes
    MEMBER = "member"                # Basic member, can view and save recipes
    GUEST = "guest"                  # Limited access, can only view public recipes

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Additional fields for premium features
    subscription_expires = Column(TIMESTAMP(timezone=True), nullable=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    owned_groups = relationship("FamilyGroup", back_populates="owner")
    group_memberships = relationship("GroupMember", back_populates="user")
    
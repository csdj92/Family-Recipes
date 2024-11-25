from sqlalchemy import Column, String, UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
import uuid

from ..models.database import Base

class User(Base):
    __tablename__ = "users"

    # Generate UUID automatically
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    role = Column(String, default='user')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    owned_groups = relationship("FamilyGroup", back_populates="owner")
    group_memberships = relationship("GroupMember", back_populates="user") 
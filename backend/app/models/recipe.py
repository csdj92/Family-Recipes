from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    ingredients = Column(JSONB, nullable=False)
    instructions = Column(String, nullable=False)
    image_url = Column(String)
    group_id = Column(UUID(as_uuid=True), ForeignKey("family_groups.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    group = relationship("FamilyGroup", back_populates="recipes") 
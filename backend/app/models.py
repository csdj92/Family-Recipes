from sqlalchemy import create_engine, Column, String, DateTime, Boolean, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from .schemas.user import UserRole

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_verified = Column(Boolean, default=False)

    # Relationships
    recipes = relationship("Recipe", back_populates="user")
    groups = relationship("FamilyGroup", secondary="group_members", back_populates="members")

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    ingredients = Column(JSONB)
    instructions = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    group_id = Column(UUID(as_uuid=True), ForeignKey("family_groups.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="recipes")
    group = relationship("FamilyGroup", back_populates="recipes")

class FamilyGroup(Base):
    __tablename__ = "family_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipes = relationship("Recipe", back_populates="group")
    members = relationship("User", secondary="group_members", back_populates="groups")

# Association table for group members
group_members = Table(
    "group_members",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("group_id", UUID(as_uuid=True), ForeignKey("family_groups.id"), primary_key=True),
    Column("joined_at", DateTime(timezone=True), server_default=func.now())
)

def create_tables():
    """Create all tables in the database"""
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/recipe_db")
    Base.metadata.create_all(bind=engine)

    # Create SessionLocal class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal 
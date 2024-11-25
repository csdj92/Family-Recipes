from .database import Base, engine
from .user import User
from .group import FamilyGroup, GroupMember
from .recipe import Recipe

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine) 
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
from .user import UserResponse

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    name: str

    class Config:
        from_attributes = True

class GroupResponse(GroupBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class GroupMemberResponse(BaseModel):
    user_id: UUID
    group_id: UUID
    joined_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True) 
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class GroupResponse(GroupBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class GroupMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    group_id: UUID
    joined_at: datetime

    class Config:
        from_attributes = True 
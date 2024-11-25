from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..dependencies import get_db
from ..services.auth import get_current_user
from ..schemas.group import GroupCreate, GroupResponse, GroupMemberResponse
from ..services.group import GroupService

router = APIRouter()

@router.post("/", response_model=GroupResponse)
async def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new family group"""
    return GroupService().create_group(db, current_user.id, group)

@router.get("/", response_model=List[GroupResponse])
async def get_user_groups(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all groups user belongs to"""
    return GroupService().get_user_groups(db, current_user.id)

@router.post("/{group_id}/members", response_model=GroupMemberResponse)
async def add_group_member(
    group_id: str,
    email: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a member to the group"""
    return GroupService().add_group_member(db, group_id, email, current_user.id)

@router.delete("/{group_id}/members/{user_id}")
async def remove_group_member(
    group_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a member from the group"""
    return GroupService().remove_group_member(db, group_id, user_id, current_user.id)
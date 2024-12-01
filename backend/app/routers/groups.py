from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ..dependencies import get_db
from ..utils.auth import get_current_user, get_user_id_from_jwt, require_role, UserRole
from ..schemas.group import GroupCreate, GroupResponse, GroupMemberResponse
from ..services.group import GroupService
from ..models.user import User
from uuid import UUID
from ..utils.cache import cache_response

router = APIRouter()

@router.post("/", response_model=GroupResponse)
async def create_group(
    group: GroupCreate,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Create a new family group"""
    user_id = get_user_id_from_jwt(token_data)
    return await GroupService().create_group(db, user_id, group)

@router.get("/", response_model=List[GroupResponse])
@cache_response(expire_time_seconds=300)  # Cache for 5 minutes
async def get_user_groups(
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Get all groups user belongs to"""
    user_id = get_user_id_from_jwt(token_data)
    return GroupService().get_user_groups(db, user_id)

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group_by_id(
    group_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Get a group by its ID"""
    user_id = get_user_id_from_jwt(token_data)
    group_service = GroupService()
    return await group_service.get_group_by_id(db, group_id)

@router.delete("/{group_id}")
async def delete_group(
    group_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Delete a family group - Only group owner or admin can delete"""
    user_id = get_user_id_from_jwt(token_data)
    return await GroupService().delete_group(db, group_id, user_id)

@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_group_members(
    group_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Get all members of a group"""
    user_id = get_user_id_from_jwt(token_data)
    return GroupService().get_group_members(db, user_id, group_id)

@router.post("/{group_id}/members", response_model=GroupMemberResponse)
async def add_group_member(
    group_id: UUID,
    email: str,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Add a member to the group"""
    user_id = get_user_id_from_jwt(token_data)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return GroupService().add_group_member(db, group_id, user.id, user_id)

@router.delete("/{group_id}/members/{user_id}")
async def remove_group_member(
    group_id: UUID,
    member_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Remove a member from the group"""
    user_id = get_user_id_from_jwt(token_data)
    return GroupService().remove_group_member(db, group_id, member_id, user_id)
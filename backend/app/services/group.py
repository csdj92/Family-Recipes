import logging
from sqlalchemy.orm import Session
from ..schemas.group import GroupCreate
from ..models.group import FamilyGroup, GroupMember
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import List
from app.models.user import User, UserRole
from ..dependencies import get_redis

logger = logging.getLogger(__name__)

class GroupService:
    async def invalidate_group_cache(self, group_id: UUID = None):
        """Invalidate group cache after modifications"""
        try:
            redis = await get_redis()
            if group_id:
                # Delete specific group cache
                await redis.delete(f"cache:/groups/{group_id}")
            # Delete list cache
            await redis.delete("cache:/groups")
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")

    async def create_group(self, db: Session, user_id: UUID, group: GroupCreate) -> FamilyGroup:
        try:
            logger.info(f"Creating new group for user {user_id}")
            group_data = group.model_dump()
            group_data["owner_id"] = user_id
            
            # Create the group
            group = FamilyGroup(**group_data)
            db.add(group)
            db.flush()  # Flush to get the group ID
            
            # Add the creator as a member
            group_member = GroupMember(
                user_id=user_id,
                group_id=group.id
            )
            db.add(group_member)
            
            db.commit()
            db.refresh(group)
            logger.info(f"Successfully created group {group.id}")
            await self.invalidate_group_cache()
            return group
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating group: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error"
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while creating group: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error"
            )
    
    def get_user_groups(self, db: Session, user_id: UUID) -> List[FamilyGroup]:
        logger.info(f"Getting all groups for user {user_id}")
        groups = db.query(FamilyGroup).filter(FamilyGroup.owner_id == user_id).all()
        logger.info(f"Found {len(groups)} groups for user {user_id}")
        return groups
    
    def get_group_by_id(self, db: Session, group_id: UUID) -> FamilyGroup:
        logger.info(f"Getting group with id {group_id}")
        group = db.query(FamilyGroup).filter(FamilyGroup.id == group_id).first()
        logger.info(f"Found group {group.id}")
        return group
    
    def add_group_member(self, db: Session, group_id: UUID, user_id: UUID, added_by_id: UUID) -> GroupMember:
        """Add a member to the group ensuring the requester has appropriate permissions"""
        # Check if the requester is the owner or has admin privileges
        requester = db.query(User).filter(User.id == added_by_id).first()
        if not requester or requester.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CREATOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add members"
            )
        
        # Check if the group exists
        group = db.query(FamilyGroup).filter(FamilyGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if the user is already a member
        existing_member = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of the group"
            )
        
        # Add the new member
        group_member = GroupMember(group_id=group_id, user_id=user_id)
        db.add(group_member)
        db.commit()
        db.refresh(group_member)
        logger.info(f"Successfully added user {user_id} to group {group_id}")
        return group_member
    
    
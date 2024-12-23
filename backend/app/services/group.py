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
import json
from ..utils.cache import get_redis

logger = logging.getLogger(__name__)

class GroupService:
    async def invalidate_group_cache(self, group_id: UUID = None):
        """Invalidate group cache after modifications"""
        try:
            redis = await get_redis()
            if group_id:
                # Delete specific group cache
                await redis.delete(f"group:{group_id}")
            # Delete list cache
            await redis.delete("cache:/groups")
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")

    async def create_group(self, db: Session, user_id: UUID, group: GroupCreate) -> FamilyGroup:
        """Create a new family group"""
        try:
            db_group = FamilyGroup(
                name=group.name,
                owner_id=user_id
            )
            db.add(db_group)
            db.commit()
            db.refresh(db_group)
            
            # Add the owner as a member
            member = GroupMember(
                user_id=user_id,
                group_id=db_group.id
            )
            db.add(member)
            db.commit()
            
            # Invalidate group list cache
            await self.invalidate_group_cache()
            
            return db_group
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating group: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not create group {e}" 
            )
    
    def get_user_groups(self, db: Session, user_id: UUID) -> List[FamilyGroup]:
        logger.info(f"Getting all groups for user {user_id}")
        groups = db.query(FamilyGroup).filter(FamilyGroup.owner_id == user_id).all()
        logger.info(f"Found {len(groups)} groups for user {user_id}")
        return groups
    
    async def get_group_by_id(self, db: Session, group_id: UUID) -> FamilyGroup:
        """Get a group by its ID"""
        cache_key = f"group:{group_id}"
        try:
            redis = await get_redis()
            cached_group = await redis.get(cache_key)
            if cached_group:
                # Parse the cached JSON string back into a FamilyGroup object
                group_data = json.loads(cached_group)
                return FamilyGroup(**group_data)
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")

        group = db.query(FamilyGroup).filter(FamilyGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Cache the group data as JSON string
        try:
            group_data = {
                "id": str(group.id),
                "name": group.name,
                "owner_id": str(group.owner_id),
                "created_at": group.created_at.isoformat()
            }
            await redis.set(cache_key, json.dumps(group_data), ex=300)
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")

        return group
    
    async def delete_group(self, db: Session, group_id: UUID, user_id: UUID) -> bool:
        """Delete a family group"""
        # Check if group exists
        group = db.query(FamilyGroup).filter(FamilyGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check if user is the owner or has admin privileges
        user = db.query(User).filter(User.id == user_id).first()
        if not user or (user.id != group.owner_id and user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only group owner or admin can delete the group"
            )
        
        try:
            # Delete all group members first
            db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
            
            # Delete the group
            db.delete(group)
            db.commit()
            
            # Invalidate cache
            await self.invalidate_group_cache(group_id)
            
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting group: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete group"
            )
    
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
    
    def get_group_members(self, db: Session, user_id: UUID, group_id: UUID) -> List[GroupMember]:
        """Get all members for group"""
        requester = db.query(User).filter(User.id == user_id).first()
        if not requester or requester.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CREATOR]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"Getting all members for group {group_id}")
        members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        logger.info(f"Found {len(members)} members for group {group_id}")
        return members  # Return GroupMember objects directly instead of user objects
    
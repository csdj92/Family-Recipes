import logging
from sqlalchemy.orm import Session
from ..schemas.group import GroupCreate
from ..models.group import FamilyGroup, GroupMember
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

logger = logging.getLogger(__name__)

class GroupService:
    def create_group(self, db: Session, user_id: UUID, group: GroupCreate) -> FamilyGroup:
        try:
            logger.info(f"Creating new group for user {user_id}")
            group_data = group.model_dump()
            group_data["owner_id"] = user_id
            
            group = FamilyGroup(**group_data)
            db.add(group)
            db.commit()
            db.refresh(group)
            logger.info(f"Successfully created group {group.id}")
            return group
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating group: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while creating group: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=str(e)
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
    
    def add_group_member(self, db: Session, group_id: UUID, user_id: UUID) -> GroupMember:
        logger.info(f"Adding user {user_id} to group {group_id}")
        group_member = GroupMember(group_id=group_id, user_id=user_id)
        db.add(group_member)
        db.commit()
        db.refresh(group_member)
        logger.info(f"Successfully added user {user_id} to group {group_id}")
        return group_member
    
    
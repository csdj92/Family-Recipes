from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..schemas.user import UserProfile, UserProfileUpdate
from ..utils.auth import get_current_user, get_user_id_from_jwt
from ..models import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Get current user's profile"""
    user_id = get_user_id_from_jwt(token_data)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    profile_update: UserProfileUpdate,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    user_id = get_user_id_from_jwt(token_data)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields if provided
    if profile_update.name is not None:
        user.name = profile_update.name
    if profile_update.email is not None:
        user.email = profile_update.email

    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile"
        ) 
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from ..schemas.user import UserCreate, UserResponse, Token
from ..utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    """
    Register a new user using Supabase Auth
    """
    try:
        # We don't need to handle signup here as it's handled by Supabase directly
        # Just return success as the trigger will create the user in our DB
        return {
            "message": "Signup should be handled by Supabase Auth directly",
            "status": "error",
            "error": "Please use Supabase signup"
        }
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(request: Request):
    """
    Login is handled by Supabase Auth directly
    This endpoint is just a placeholder
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please use Supabase Auth for login"
    )

@router.post("/logout")
async def logout(request: Request):
    """
    Logout is handled by Supabase Auth directly
    This endpoint is just a placeholder
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Please use Supabase Auth for logout"
    )
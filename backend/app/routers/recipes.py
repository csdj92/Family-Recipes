from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..dependencies import get_db
from ..services.auth import (
    get_current_user,
    get_creator_or_above,
    get_premium_user,
    get_admin_or_above
)
from ..services import recipe as recipe_service
from ..schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from ..models.user import User, UserRole
from ..utils.cache import cache_response

router = APIRouter()

@router.post("/", response_model=RecipeResponse)
async def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_creator_or_above)
):
    """Create a new recipe - Requires CREATOR role or above"""
    return recipe_service.create_recipe(db, recipe, current_user.id)

@router.get("/", response_model=List[RecipeResponse])
@cache_response(expire_time_seconds=300)
async def get_recipes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recipes for user's groups - All authenticated users"""
    if current_user.role == UserRole.GUEST:
        # Guests can only see public recipes
        return recipe_service.get_public_recipes(db, skip, limit)
    return recipe_service.get_user_recipes(db, current_user.id, skip, limit)

@router.get("/all", response_model=List[RecipeResponse])
async def get_all_recipes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_above)
):
    """Get all recipes in the system - Admin only"""
    return recipe_service.get_all_recipes(db, current_user.id, skip, limit)

@router.get("/{recipe_id}", response_model=RecipeResponse)
@cache_response(expire_time_seconds=300)
async def get_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recipe - Access controlled by group membership"""
    return recipe_service.get_recipe_by_id(db, recipe_id, current_user.id)

@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_creator_or_above)
):
    """Update a recipe - Requires CREATOR role or above and group membership"""
    return recipe_service.update_recipe(db, recipe_id, recipe, current_user.id)

@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_creator_or_above)
):
    """Delete a recipe - Requires CREATOR role or above and group membership"""
    recipe_service.delete_recipe(db, recipe_id, current_user.id)
    return {"message": "Recipe deleted successfully"}

@router.post("/parse-image")
async def parse_recipe_from_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_premium_user)
):
    """Parse recipe from uploaded image - Premium feature"""
    return await recipe_service.parse_recipe_image(db, image, current_user.id)

@router.post("/{recipe_id}/feature")
async def feature_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_or_above)
):
    """Feature a recipe - Admin only"""
    return recipe_service.feature_recipe(db, current_user.id, recipe_id)
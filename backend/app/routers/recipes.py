from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..dependencies import get_db
from ..services import recipe as recipe_service
from ..schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from ..utils.cache import cache_response
from ..utils.auth import get_current_user, get_user_id_from_jwt, require_role, UserRole

router = APIRouter()

@router.post("/", response_model=RecipeResponse)
async def create_recipe(
    recipe: RecipeCreate,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role(UserRole.MEMBER, UserRole.PREMIUM, UserRole.CREATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN))
):
    """Create a new recipe - Requires MEMBER role or above"""
    user_id = get_user_id_from_jwt(token_data)
    return recipe_service.create_recipe(db, recipe, user_id)

@router.get("/", response_model=List[RecipeResponse])
@cache_response(expire_time_seconds=300)
async def get_recipes(
    request: Request,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Get all recipes for user's groups - Any authenticated user"""
    user_id = get_user_id_from_jwt(token_data)
    return recipe_service.get_user_recipes(db, user_id, skip, limit)

@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user)
):
    """Get a specific recipe - Any authenticated user"""
    user_id = get_user_id_from_jwt(token_data)
    return await recipe_service.get_recipe_by_id(db, recipe_id, user_id)

@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: UUID,
    recipe_update: RecipeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role(UserRole.MEMBER, UserRole.PREMIUM, UserRole.CREATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN))
):
    """Update a recipe - Requires MEMBER role or above"""
    user_id = get_user_id_from_jwt(token_data)
    return await recipe_service.update_recipe(db, recipe_id, recipe_update, user_id)

@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role(UserRole.MEMBER, UserRole.PREMIUM, UserRole.CREATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN))
):
    """Delete a recipe - Requires MEMBER role or above"""
    user_id = get_user_id_from_jwt(token_data)
    return await recipe_service.delete_recipe(db, recipe_id, user_id)

@router.post("/parse-image")
async def parse_recipe_from_image(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role(UserRole.PREMIUM, UserRole.ADMIN, UserRole.SUPER_ADMIN))
):
    """Parse recipe from uploaded image - Requires PREMIUM or above"""
    user_id = get_user_id_from_jwt(token_data)
    return await recipe_service.parse_recipe_image(db, image, user_id)
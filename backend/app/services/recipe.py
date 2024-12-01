from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from uuid import UUID
from typing import List
import asyncio
import json

from ..models.recipe import Recipe
from ..models.group import GroupMember
from ..schemas.recipe import RecipeCreate, RecipeUpdate
from ..dependencies import get_redis
from ..utils.cache import get_redis
import logging

logger = logging.getLogger(__name__)

def check_recipe_access(db: Session, recipe_id: UUID, user_id: UUID) -> bool:
    """Check if user has access to the recipe through group membership"""
    return db.query(Recipe).join(
        GroupMember, Recipe.group_id == GroupMember.group_id
    ).filter(
        Recipe.id == recipe_id,
        GroupMember.user_id == user_id
    ).first() is not None

async def invalidate_recipe_cache(recipe_id: UUID = None):
    """Invalidate recipe cache after modifications"""
    try:
        redis = await get_redis()
        try:
            if recipe_id:
                # Delete specific recipe cache
                await redis.delete(f"recipe:{recipe_id}")
            # Delete list cache if applicable
            await redis.delete("cache:/recipes")
        finally:
            await redis.close()
    except Exception as e:
        logger.error(f"Cache invalidation error: {str(e)}")

def create_recipe(db: Session, recipe: RecipeCreate, user_id: UUID) -> Recipe:
    """Create a new recipe after verifying user is member of the group"""
    # Check if user is member of the group
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == recipe.group_id,
        GroupMember.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of this group"
        )
    
    db_recipe = Recipe(
        title=recipe.title,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        image_url=recipe.image_url,
        group_id=recipe.group_id
    )
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    # Run cache invalidation in the background
    asyncio.create_task(invalidate_recipe_cache())
    return db_recipe

def get_public_recipes(db: Session, skip: int = 0, limit: int = 10) -> List[Recipe]:
    """Get public recipes only"""
    return db.query(Recipe).filter(
        Recipe.is_public == True
    ).offset(skip).limit(limit).all()

def get_user_recipes(db: Session, user_id: UUID, skip: int = 0, limit: int = 10) -> List[Recipe]:
    """Get all recipes from groups user is member of"""
    return db.query(Recipe).join(
        GroupMember, Recipe.group_id == GroupMember.group_id
    ).filter(
        GroupMember.user_id == user_id
    ).offset(skip).limit(limit).all()

def get_all_recipes(db: Session, user_id: UUID = None, skip: int = 0, limit: int = 10) -> List[Recipe]:
    """Get all recipes in the system - Admin only"""
    return db.query(Recipe).offset(skip).limit(limit).all()

async def get_recipe_by_id(db: Session, recipe_id: UUID, user_id: UUID) -> Recipe:
    """Get a specific recipe if user has access"""
    cache_key = f"recipe:{recipe_id}"
    try:
        redis = await get_redis()
        cached_recipe = await redis.get(cache_key)
        if cached_recipe:
            return Recipe.parse_raw(cached_recipe)
    except Exception as e:
        logger.error(f"Cache retrieval error: {str(e)}")

    # Fetch from database
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user has access through group membership
    if not check_recipe_access(db, recipe_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Cache the recipe
    try:
        await redis.set(cache_key, recipe.json(), ex=300)  # Cache for 5 minutes
    except Exception as e:
        logger.error(f"Cache set error: {str(e)}")

    return recipe

async def update_recipe(db: Session, recipe_id: UUID, recipe_update: RecipeUpdate, user_id: UUID) -> Recipe:
    """Update a recipe if user has access"""
    # Check if recipe exists and user has access
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user has access through group membership
    if not check_recipe_access(db, recipe_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update recipe attributes
    for var, value in vars(recipe_update).items():
        if value is not None:
            setattr(recipe, var, value)
    
    try:
        db.commit()
        db.refresh(recipe)
        await invalidate_recipe_cache(recipe_id)
        return recipe
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating recipe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recipe"
        )

async def delete_recipe(db: Session, recipe_id: UUID, user_id: UUID) -> bool:
    """Delete a recipe if user has access"""
    # First check if recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if user has access through group membership
    if not check_recipe_access(db, recipe_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Delete the recipe
        db.delete(recipe)
        db.commit()
        # Invalidate cache
        await invalidate_recipe_cache(recipe_id)
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting recipe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recipe"
        )

async def parse_recipe_image(db: Session, image: UploadFile, user_id: UUID):
    """Parse recipe from image - Premium feature"""
    # TODO: Implement GPT-4 Vision integration
    pass

def feature_recipe(db: Session, recipe_id: UUID) -> Recipe:
    """Feature a recipe - Admin only"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    recipe.is_featured = True
    db.commit()
    db.refresh(recipe)
    return recipe 
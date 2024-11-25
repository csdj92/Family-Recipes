from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from uuid import UUID
from typing import List

from ..models.recipe import Recipe
from ..models.group import GroupMember
from ..schemas.recipe import RecipeCreate, RecipeUpdate

def check_recipe_access(db: Session, recipe_id: UUID, user_id: UUID) -> bool:
    """Check if user has access to the recipe through group membership"""
    return db.query(Recipe).join(
        GroupMember, Recipe.group_id == GroupMember.group_id
    ).filter(
        Recipe.id == recipe_id,
        GroupMember.user_id == user_id
    ).first() is not None

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

def get_recipe_by_id(db: Session, recipe_id: UUID, user_id: UUID) -> Recipe:
    """Get a specific recipe if user has access"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # Check if recipe is public
    if recipe.is_public:
        return recipe
        
    # Check if user has access through group membership
    if not check_recipe_access(db, recipe_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return recipe

def update_recipe(db: Session, recipe_id: UUID, recipe_update: RecipeUpdate, user_id: UUID) -> Recipe:
    """Update a recipe if user has access"""
    recipe = get_recipe_by_id(db, recipe_id, user_id)
    
    # Update recipe attributes
    for var, value in vars(recipe_update).items():
        if value is not None:
            setattr(recipe, var, value)
    
    db.commit()
    db.refresh(recipe)
    return recipe

def delete_recipe(db: Session, recipe_id: UUID, user_id: UUID) -> bool:
    """Delete a recipe if user has access"""
    recipe = get_recipe_by_id(db, recipe_id, user_id)
    
    db.delete(recipe)
    db.commit()
    return True

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
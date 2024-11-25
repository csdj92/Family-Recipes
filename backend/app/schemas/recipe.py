from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from uuid import UUID

class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    image_url: Optional[str] = None

class RecipeCreate(RecipeBase):
    group_id: UUID

class RecipeUpdate(RecipeBase):
    pass

class RecipeResponse(RecipeBase):
    id: UUID
    group_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 
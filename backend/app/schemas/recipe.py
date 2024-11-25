from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import bleach

def sanitize_html(value):
    if isinstance(value, list):
        return [bleach.clean(str(item)) for item in value]
    return bleach.clean(str(value))

class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str
    image_url: Optional[str] = None

class RecipeCreate(RecipeBase):
    group_id: UUID

    @field_validator('title', 'ingredients', 'instructions')
    @classmethod
    def sanitize_input(cls, v):
        return sanitize_html(v)

class RecipeUpdate(RecipeBase):
    pass

class RecipeResponse(RecipeBase):
    id: UUID
    group_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 
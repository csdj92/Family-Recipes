import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app
from app.models.user import User, UserRole
from app.models.group import FamilyGroup, GroupMember
from app.dependencies import get_db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def test_create_recipe(client, test_db):
    # Authenticate and obtain token
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash=get_password_hash("testpass123"),
        role=UserRole.CREATOR  # Assign a role that has permission
    )
    test_db.add(user)
    test_db.commit()

    group = FamilyGroup(
        name="Test Group",
        owner_id=user.id
    )
    test_db.add(group)
    test_db.commit()

    member = GroupMember(
        user_id=user.id,
        group_id=group.id
    )
    test_db.add(member)
    test_db.commit()

    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]

    # Attempt to create a recipe without the token
    recipe_data = {
        "title": "Unauthorized Recipe",
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": "Test instructions",
        "group_id": str(group.id)
    }
    response = client.post(
        "/recipes/",
        json=recipe_data
    )
    assert response.status_code == 401  # Unauthorized

    # Create recipe with valid token
    recipe_data["title"] = "Authorized Recipe"
    response = client.post(
        "/recipes/",
        headers={"Authorization": f"Bearer {token}"},
        json=recipe_data
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == recipe_data["title"] 
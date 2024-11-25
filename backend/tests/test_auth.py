from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.dependencies import get_db

client = TestClient(app)

def clear_users():
    db = next(get_db())
    db.query(User).delete()
    db.commit()

def test_signup():
    # Clear the database first
    clear_users()
    
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    print(f"Signup response: {response.content}")
    assert response.status_code == 200
    assert "id" in response.json()

def test_login():
    # Clear the database first
    clear_users()
    
    # First ensure we have a user to login with
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    
    # Then try to login using form data
    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    print(f"Login response: {response.content}")
    assert response.status_code == 200
    assert "access_token" in response.json() 
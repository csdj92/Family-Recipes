from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_google_oauth_client,
    get_password_hash
)
from ..schemas.user import UserCreate, UserResponse, Token
from ..models.user import User

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user's information"""
    return current_user

@router.get("/google/login")
async def google_login():
    client = get_google_oauth_client()
    redirect_uri = client.create_authorization_url()
    return {"url": redirect_uri}

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    client = get_google_oauth_client()
    token = client.fetch_token(code=code)
    user_info = client.get_user_info(token)
    
    # Check if user exists, if not create new user
    db_user = db.query(User).filter(User.email == user_info["email"]).first()
    if not db_user:
        db_user = User(
            email=user_info["email"],
            name=user_info["name"],
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
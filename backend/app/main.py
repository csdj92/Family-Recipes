from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, recipes, groups
from .models import create_tables

app = FastAPI(title="Recipe Sharing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])
app.include_router(groups.router, prefix="/groups", tags=["Family Groups"])

@app.get("/")
async def root():
    return {"message": "Welcome to Recipe Sharing API"} 
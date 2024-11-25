from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .routers import auth, recipes, groups
from .models import create_tables, User
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from .config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup - Initialize FastAPILimiter with Redis
    try:
        redis = await aioredis.from_url(
            settings.REDIS_URL or "redis://localhost",
            encoding="utf8",
            decode_responses=True
        )
        await FastAPILimiter.init(redis)
        yield
    except Exception as e:
        # Log the error but allow the application to start
        print(f"Warning: Rate limiting is disabled - {str(e)}")
        yield
    finally:
        # Cleanup
        if 'redis' in locals():
            await redis.close()

app = FastAPI(
    title="Recipe Sharing API",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "https://your-frontend-domain.com",
    "https://staging.your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

# Add TrustedHost middleware after routers
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "api.yourdomain.com",
        "localhost",
        "127.0.0.1",
        "0.0.0.0"
    ]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Recipe Sharing API"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

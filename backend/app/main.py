from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .routers import auth, recipes, groups, users
from .models import Base
from .dependencies import engine
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from .config import get_settings
from .utils.auth import verify_supabase_jwt
import logging

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

async def get_redis():
    return await aioredis.from_url(
        settings.REDIS_URL or "redis://localhost",
        encoding="utf8",
        decode_responses=True
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Setup - Initialize FastAPILimiter with Redis
    try:
        redis = await get_redis()
        await FastAPILimiter.init(redis)
        yield
    except Exception as e:
        logger.error(f"Service initialization error: {str(e)}")
        yield
    finally:
        if 'redis' in locals():
            await redis.close()

app = FastAPI(
    title="Recipe Sharing API",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vue.js development server
    "http://localhost:4173",  # Vue.js preview server
    "http://localhost:3000",  # Optional: For other development scenarios
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "apikey",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "Access-Control-Allow-Origin"
    ],
    expose_headers=["*"],
    max_age=86400  # Cache preflight requests for 24 hours
)

@app.middleware("http")
async def supabase_auth_middleware(request: Request, call_next):
    # Skip auth for public endpoints and OPTIONS requests
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"] or request.method == "OPTIONS":
        return await call_next(request)

    try:
        # Verify JWT token
        token_data = await verify_supabase_jwt(request)
        if token_data:
            # Add user data to request state
            request.state.user = token_data
    except HTTPException as e:
        # Skip auth errors for auth endpoints
        if not request.url.path.startswith("/auth/"):
            raise e

    response = await call_next(request)
    return response

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(recipes.router, prefix="/recipes", tags=["Recipes"])
app.include_router(groups.router, prefix="/groups", tags=["Family Groups"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# Add TrustedHost middleware after routers
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "0.0.0.0"
    ]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Recipe Sharing API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis = await get_redis()
        await redis.ping()
        redis_status = "connected"
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        redis_status = "error"
    finally:
        if 'redis' in locals():
            await redis.close()
            
    return {
        "status": "healthy",
        "version": "1.0.0",
        "redis": redis_status
    }

"""FastAPI application"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .utils.logger import setup_logging, get_logger
from .services.redis_service import RedisService
from .services.llm_service import LLMService
from .api.routes import router, set_services
from .api.dependencies import verify_api_key

# Setup logging
setup_logging(log_level=settings.log_level, json_output=settings.log_json)
logger = get_logger(__name__)

# Global services - will be initialized in lifespan
redis_service: Optional[RedisService] = None
llm_service: Optional[LLMService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global redis_service, llm_service

    # Startup
    logger.info("Starting WebSketch Agent Service")
    redis_service = RedisService(redis_url=settings.redis_url)
    llm_service = LLMService(
        api_key=settings.openai_api_key,
        model_name=settings.openai_model,
        temperature=settings.openai_temperature,
    )
    await redis_service.connect()

    # Set services in routes module to avoid circular import
    set_services(redis_service, llm_service)

    logger.info("Service started successfully")
    yield
    # Shutdown
    logger.info("Shutting down WebSketch Agent Service")
    if redis_service:
        await redis_service.disconnect()
    logger.info("Service shut down")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "WebSketch Agent API",
        "version": settings.api_version,
        "status": "running",
    }


from datetime import datetime
from fastapi import APIRouter, Request
from loguru import logger
from models.schemas import HealthResponse
from config.settings import settings
from app.routers import auth, conversation, review

router = APIRouter()

# Include sub-routers
router.include_router(auth.router)
router.include_router(review.router)
router.include_router(conversation.router)


@router.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    try:
        logger.info("Initializing Application...")
        settings.validate_settings()
        logger.success("Application initialized successfully!")
    except Exception as e:
        logger.critical(f"Failed to initialize Application: {e}", exc_info=True)
        raise


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /health from {client_ip}")
    
    response = HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )
    
    logger.info(f"RESPONSE /health: {response.status}")
    return response



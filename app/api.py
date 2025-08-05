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




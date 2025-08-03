from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, APIRouter, Request, status, Depends
from loguru import logger
from models.schemas import LoginRequest, LoginResponse, UserCreateRequest, SignupResponse
from config.container import Container
from ..dependencies import get_auth_service
from services.auth_service import AuthService


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/signup", status_code=status.HTTP_200_OK, response_model=SignupResponse)
def signup(
    request: UserCreateRequest,
    auth_service = Depends(get_auth_service)
) -> SignupResponse:
    """ Create a new user account.
    """
    try:
        logger.info(f"REQUEST /auth/signup - Email: {request.email}, Username: {request.username}")
        
        # Create new user using injected service
        user_id = auth_service.create_user(request.email, request.username, request.password)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User creation failed")
        
        logger.info(f"RESPONSE /auth/signup: User {request.username} created successfully with ID {user_id}")
        return SignupResponse(message="User created successfully", user_id=user_id)
        
    except HTTPException:
        logger.error(f"HTTPException during signup: {request}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error during signup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during signup")
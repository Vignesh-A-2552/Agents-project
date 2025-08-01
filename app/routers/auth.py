from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, APIRouter, Request, Depends
from loguru import logger
from models.schemas import LoginRequest, LoginResponse
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user, get_current_admin_user
from config.settings import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Initialize auth service
auth_service = AuthService()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, http_request: Request):
    """
    Authenticate user and return JWT access token.
    
    - **username**: Username or email
    - **password**: User password
    
    Default users:
    - admin/admin123 (admin role)
    - user/user123 (user role)
    """
    client_ip = http_request.client.host if http_request.client else "unknown"
    logger.info(f"REQUEST /auth/login from {client_ip} - Username: {request.username}")
    
    try:
        # Authenticate user
        user = auth_service.authenticate_user(request.username, request.password)
        if not user:
            logger.warning(f"Failed login attempt for username: {request.username} from {client_ip}")
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        user_info = auth_service.get_user_info(user)
        
        response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_HOURS * 3600,  # Convert hours to seconds
            user_info=user_info.dict()
        )
        
        logger.info(f"RESPONSE /auth/login: Successful login for {request.username} from {client_ip}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during login")


@router.get("/profile")
async def get_user_profile(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile. Requires authentication."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /auth/profile from {client_ip} - User: {current_user.get('username')}")
    
    response = {
        "user_id": current_user.get("user_id"),
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "token_expires": current_user.get("exp")
    }
    
    logger.info(f"RESPONSE /auth/profile: Profile for user {current_user.get('username')}")
    return response


@router.post("/logout")
async def logout(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout user (client-side token removal)."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /auth/logout from {client_ip} - User: {current_user.get('username')}")
    
    response = {
        "message": "Successfully logged out",
        "user": current_user.get("username")
    }
    
    logger.info(f"RESPONSE /auth/logout: User {current_user.get('username')} logged out")
    return response


@router.get("/verify")
async def verify_token(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verify if current token is valid."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /auth/verify from {client_ip} - User: {current_user.get('username')}")
    
    response = {
        "valid": True,
        "user": {
            "user_id": current_user.get("user_id"),
            "username": current_user.get("username"),
            "role": current_user.get("role"),
            "expires": current_user.get("exp")
        }
    }
    
    logger.info(f"RESPONSE /auth/verify: Token valid for user {current_user.get('username')}")
    return response


@router.get("/admin/stats")
async def get_admin_stats(request: Request, current_user: Dict[str, Any] = Depends(get_current_admin_user)):
    """Get system statistics. Requires admin role."""
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"REQUEST /auth/admin/stats from {client_ip} - Admin: {current_user.get('username')}")
    
    # Mock statistics - in real app, these would come from database
    response = {
        "total_users": 2,
        "total_reviews": 0,
        "system_uptime": "Just started",
        "admin_user": current_user.get("username"),
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"RESPONSE /auth/admin/stats: Statistics retrieved by admin {current_user.get('username')}")
    return response
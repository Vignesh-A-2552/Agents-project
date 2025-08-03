from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, APIRouter, Request, status
from loguru import logger
from models.schemas import LoginRequest, LoginResponse, UserCreateRequest, SignupResponse
from services.auth_service import AuthService
from Infrastructure.client.AuthRepository import AuthRepository
from config.settings import settings


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Initialize auth service
# auth_service = AuthService()


# login")@router.post("/login", response_model=LoginResponse)
# async def login(request: LoginRequest, http_request: Request):
#     """
#     Authenticate user and return JWT access token.
    
#     - **username**: Username or email
#     - **password**: User password
    
#     Default users:
#     - admin/admin123 (admin role)
#     - user/user123 (user role)
#     """
#     client_ip = http_request.client.host if http_request.client else "unknown"
#     logger.info(f"REQUEST /auth/login from {client_ip} - Username: {request.username}")
    
#     try:
#         # Authenticate user
#         user = auth_service.authenticate_user(request.username, request.password)
#         if not user:
#             logger.warning(f"Failed login attempt for username: {request.username} from {client_ip}")
#             raise HTTPException(
#                 status_code=401,
#                 detail="Invalid username or password"
#             )
        
#         # Create access token
#         access_token = auth_service.create_access_token(user)
#         user_info = auth_service.get_user_info(user)
        
#         response = LoginResponse(
#             access_token=access_token,
#             token_type="bearer",
#             expires_in=settings.JWT_EXPIRATION_HOURS * 3600,  # Convert hours to seconds
#             user_info=user_info.dict()
#         )
        
#         logger.info(f"RESPONSE /auth/login: Successful login for {request.username} from {client_ip}")
#         return response
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error during login: {e}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Internal server error during login")


@router.post("/signup", status_code=status.HTTP_200_OK, response_model=SignupResponse)
def signup(request: UserCreateRequest) -> SignupResponse:
    """ Create a new user account.
    """
    try:
        logger.info(f"REQUEST /auth/signup - Email: {request.email}, Username: {request.username}")
        
        # Create auth service instance
        auth_repo = AuthRepository(settings.DATABASE_URL)
        auth_service = AuthService(auth_repo)
        
        # Create new user
        user_id = auth_service.create_user(request.email, request.username, request.password)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User creation failed")
        
        logger.info(f"RESPONSE /auth/signup: User {request.username} created successfully with ID {user_id}")
        return SignupResponse(message="User created successfully", user_id=user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during signup")
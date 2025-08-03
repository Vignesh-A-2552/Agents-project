from fastapi import HTTPException, APIRouter, status, Depends
from loguru import logger
from models.schemas import LoginRequest, LoginResponse, UserCreateRequest, SignupResponse
from ..dependencies import get_auth_service


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

@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
def login(
    request: LoginRequest,
    auth_service = Depends(get_auth_service)
) -> LoginResponse:
    """ Authenticate user and return access and refresh tokens.
    """
    try:
        logger.info(f"REQUEST /auth/login - Email: {request.email}")
        
        # Authenticate user using injected service
        auth_result = auth_service.authenticate_user(request.email, request.password)
        
        if not auth_result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        logger.info(f"RESPONSE /auth/login: User {request.email} logged in successfully")
        return LoginResponse(
            access_token=auth_result['access_token'],
            refresh_token=auth_result['refresh_token'],
            token_type=auth_result['token_type'],
            expires_in=auth_result['expires_in']
        )
        
    except HTTPException:
        logger.error(f"HTTPException during login: {request}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during login")
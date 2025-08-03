from typing import Optional, Dict, Any
from Interface.auth_interface import AuthServiceInterface
from config.settings import settings

class AuthService:
    def __init__(self, repo: AuthServiceInterface):
        self.repo = repo

    def create_user(self, email: str, username: str, password: str) -> str:
        return self.repo.create_user(email, username, password)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_user_by_email(email)

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_email(email)
        if user and self.repo.verify_password(password, user.get('password_hash', '')):
            # Generate both access and refresh tokens
            secret_key = settings.JWT_SECRET_KEY
            algorithm = settings.JWT_ALGORITHM
            expiration = settings.JWT_EXPIRATION_HOURS
            access_token = self.repo.generate_access_token(user, secret_key, algorithm, expiration)
            refresh_token = self.repo.generate_refresh_token(user, secret_key, algorithm)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': expiration * 3600  # Convert hours to seconds
            }
        return None
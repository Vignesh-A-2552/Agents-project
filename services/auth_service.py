import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from models.schemas import UserInfo
from config.settings import settings


class AuthService:
    """Authentication service for handling user login and JWT tokens."""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_hours = settings.JWT_EXPIRATION_HOURS
        
        # Simple in-memory user store for demo
        # In production, this should be a proper database
        self.users = {
            "admin": {
                "user_id": "1",
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": self._hash_password("admin123"),
                "role": "admin",
                "created_at": datetime.now(),
                "last_login": None
            },
            "user": {
                "user_id": "2", 
                "username": "user",
                "email": "user@example.com",
                "password_hash": self._hash_password("user123"),
                "role": "user",
                "created_at": datetime.now(),
                "last_login": None
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password."""
        user = self.users.get(username)
        if not user:
            return None
        
        password_hash = self._hash_password(password)
        if password_hash != user["password_hash"]:
            return None
        
        # Update last login
        user["last_login"] = datetime.now()
        return user
    
    def create_access_token(self, user: Dict[str, Any]) -> str:
        """Create JWT access token for user."""
        payload = {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_info(self, user: Dict[str, Any]) -> UserInfo:
        """Convert user dict to UserInfo model."""
        return UserInfo(
            user_id=user["user_id"],
            username=user["username"],
            email=user.get("email"),
            role=user["role"],
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
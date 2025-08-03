
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class AuthServiceInterface(ABC):
    @abstractmethod
    def create_user(self, email: str, username: str, password: str) -> str:
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass
    
    @abstractmethod
    def generate_access_token(self, user_data: Dict[str, Any], secret_key: str, algorithm: str, expiration_hours: int = 24) -> str:
        pass
    
    @abstractmethod
    def generate_refresh_token(self, user_data: Dict[str, Any], secret_key: str, algorithm: str) -> str:
        pass

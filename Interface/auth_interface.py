
from abc import ABC, abstractmethod


class AuthServiceInterface(ABC):
    @abstractmethod
    def create_user(self, email: str, username: str, password: str) -> str:
        pass

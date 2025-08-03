from models.schemas import UserCreateRequest
from Interface.auth_interface import AuthServiceInterface

class AuthService:
    def __init__(self, repo: AuthServiceInterface):
        self.repo = repo

    def create_user(self, email: str, username: str, password: str):
        # Logic to create a new user in the database
        return self.repo.create_user(email, username, password)

    def get_user_by_email(self, email: str):
        # Logic to retrieve a user by email
        pass

    def get_user_by_username(self, username: str):
        # Logic to retrieve a user by username
        pass
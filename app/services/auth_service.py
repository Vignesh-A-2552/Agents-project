from typing import Optional, Dict, Any
from Interface.auth_interface import AuthServiceInterface
from config.settings import settings

# JWT configuration
secret_key = settings.JWT_SECRET_KEY
algorithm = settings.JWT_ALGORITHM
expiration = settings.JWT_EXPIRATION_HOURS
class AuthService:
    def __init__(self, repo: AuthServiceInterface):
        """
        Initialize the AuthService with a repository that implements AuthServiceInterface.
        """
        self.repo = repo

    def create_user(self, email: str, username: str, password: str) -> str:
        """        
        Create a new user in the system.
        This method hashes the password and stores the user details in the database.
        Args:
            email (str): The email address of the user.
            username (str): The username of the user.
            password (str): The password of the user.
        Returns:
            str: The ID of the created user.
        Raises:
            ValueError: If password hashing fails or user creation fails in the database.
        """
        return self.repo.create_user(email, username, password)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user details by email.
        This method queries the repository for a user with the given email address.
        Args:
            email (str): The email address of the user to retrieve.
        Returns:
            Optional[Dict[str, Any]]: User details if found, otherwise None.
        """
        return self.repo.get_user_by_email(email)

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by email and password.
        This method verifies the user's credentials and generates JWT tokens if successful.
        Args:
            email (str): The email address of the user.
            password (str): The password of the user.
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing the access and refresh tokens if authentication is successful, otherwise None.
        """
        user = self.get_user_by_email(email)
        if user and self.repo.verify_password(password, user.get('password_hash', '')):
            # Generate both access and refresh tokens
            access_token = self.repo.generate_access_token(user, secret_key, algorithm, expiration)
            refresh_token = self.repo.generate_refresh_token(user, secret_key, algorithm)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': expiration * 3600  # Convert hours to seconds
            }
        return None
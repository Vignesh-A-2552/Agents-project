import bcrypt
from Infrastructure.db.BasePostgresRepostiory import BasePostgresRepository
from Interface.auth_interface import AuthServiceInterface

class AuthRepository(AuthServiceInterface, BasePostgresRepository):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def create_user(self, email: str, username: str, password: str) -> str:
        """Create a new user in the database."""
        hashed_password = self.hash_password(password)
        if not hashed_password:
            raise ValueError("Password hashing failed")
        
        # Use BasePostgresRepository's execute_returning_command for RETURNING queries
        query = """
        INSERT INTO users (user_name, password, email)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        params = (username, hashed_password, email)
        result = self.execute_returning_command(query, params)
        
        if result and len(result) > 0:
            return str(result[0]['id'])
        else:
            raise ValueError("Failed to create user")
    
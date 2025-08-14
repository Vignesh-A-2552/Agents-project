from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt

from app.Infrastructure.db.BasePostgresRepository import BasePostgresRepository
from app.Interface.auth_interface import AuthServiceInterface

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
        INSERT INTO users(user_name, password, email)
        VALUES(%s, %s, %s)
        RETURNING id;
        """
        params = (username, hashed_password, email)
        result = self.execute_returning_command(query, params)

        if result and len(result) > 0:
            return str(result[0]['id'])
        else:
            raise ValueError("Failed to create user")

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by email address."""
        query = """
        SELECT id, user_name as username, email, password as password_hash
        FROM users
        WHERE email = %s;
        """
        params = (email, )
        results = self.execute_query(query, params)

        if results and len(results) > 0:
            return results[0]
        return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash."""
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def generate_access_token(self, user_data: Dict[str, Any], secret_key: str, algorithm: str, expiration_hours: int=24) -> str:
        """Generate JWT access token."""
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'username': user_data.get('username'),
            'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
            'iat': datetime.utcnow(),
            'type': 'access'
        }

        return jwt.encode(payload, secret_key, algorithm)

    def generate_refresh_token(self, user_data: Dict[str, Any], secret_key: str, algorithm: str) -> str:
        """Generate JWT refresh token."""
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }

        # Use a secure secret key(should be from environment variables in production
        return jwt.encode(payload, secret_key, algorithm)

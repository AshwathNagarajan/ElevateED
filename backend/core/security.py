"""
Secure token management with JWT access and refresh tokens.
Implements short-lived access tokens and long-lived refresh tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from config import settings
from core.logging import logger
from uuid import uuid4


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenManager:
    """
    Manages JWT access and refresh tokens with expiration and type checking.
    """
    
    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS = 7    # 7 days
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
        
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        user_id: int,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a short-lived JWT access token.
        
        Args:
            user_id: User ID
            role: User role (admin, mentor, student)
            expires_delta: Optional custom expiration time
        
        Returns:
            JWT access token
        """
        to_encode = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid4())
        }
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        logger.info(
            f"Access token created for user {user_id}",
            extra={"user_id": user_id, "expires_in_minutes": TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES}
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        Create a long-lived JWT refresh token.
        
        Args:
            user_id: User ID
        
        Returns:
            JWT refresh token
        """
        to_encode = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid4())
        }
        
        expire = datetime.now(timezone.utc) + timedelta(
            days=TokenManager.REFRESH_TOKEN_EXPIRE_DAYS
        )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        logger.info(
            f"Refresh token created for user {user_id}",
            extra={"user_id": user_id, "expires_in_days": TokenManager.REFRESH_TOKEN_EXPIRE_DAYS}
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(
        token: str,
        token_type: str = "access"
    ) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")
        
        Returns:
            Token payload as dictionary
        
        Raises:
            HTTPException: If token is invalid, expired, or wrong type
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                logger.warning(
                    f"Token type mismatch: expected {token_type}, got {payload.get('type')}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
    
    @staticmethod
    def extract_user_id(token: str) -> int:
        """
        Extract user ID from token without full verification.
        
        Args:
            token: JWT token
        
        Returns:
            User ID
        
        Raises:
            HTTPException: If token is malformed
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Don't verify expiration for extraction
            )
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("No user ID in token")
            return int(user_id)
        except Exception as e:
            logger.error(f"Failed to extract user ID from token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not extract user information from token"
            )


__all__ = [
    'TokenManager',
    'pwd_context'
]

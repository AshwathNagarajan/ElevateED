"""
Token blacklist service for managing revoked tokens.
"""

import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from models.token_blacklist import TokenBlacklist
from core.logging import logger


class TokenBlacklistService:
    """
    Manages token blacklisting for logout and revocation.
    """
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash token to save space in database"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def add_to_blacklist(
        token: str,
        user_id: int,
        expires_at: datetime,
        db: Session
    ) -> None:
        """
        Add token to blacklist (e.g., on logout).
        
        Args:
            token: JWT token to blacklist
            user_id: User ID
            expires_at: Token expiration datetime
            db: Database session
        """
        token_hash = TokenBlacklistService._hash_token(token)
        
        # Check if already blacklisted
        existing = db.query(TokenBlacklist).filter(
            TokenBlacklist.token_hash == token_hash
        ).first()
        
        if existing:
            logger.warning(f"Token already blacklisted for user {user_id}")
            return
        
        blacklist_entry = TokenBlacklist(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        
        db.add(blacklist_entry)
        db.commit()
        
        logger.info(
            f"Token blacklisted for user {user_id}",
            extra={"user_id": user_id}
        )
    
    @staticmethod
    def is_blacklisted(token: str, db: Session) -> bool:
        """
        Check if token is blacklisted.
        
        Args:
            token: JWT token to check
            db: Database session
        
        Returns:
            True if token is blacklisted, False otherwise
        """
        token_hash = TokenBlacklistService._hash_token(token)
        
        blacklist_entry = db.query(TokenBlacklist).filter(
            TokenBlacklist.token_hash == token_hash
        ).first()
        
        return blacklist_entry is not None
    
    @staticmethod
    def cleanup_expired(db: Session) -> int:
        """
        Remove expired tokens from blacklist.
        Should be called periodically (e.g., daily via Celery task).
        
        Args:
            db: Database session
        
        Returns:
            Number of tokens removed
        """
        expired_count = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        
        if expired_count > 0:
            logger.info(
                f"Cleaned up {expired_count} expired tokens from blacklist"
            )
        
        return expired_count
    
    @staticmethod
    def revoke_all_user_tokens(user_id: int, db: Session) -> int:
        """
        Revoke all tokens for a user (e.g., password change, security breach).
        
        Args:
            user_id: User ID
            db: Database session
        
        Returns:
            Number of tokens revoked
        """
        revoked_count = db.query(TokenBlacklist).filter(
            TokenBlacklist.user_id == user_id
        ).delete()
        
        db.commit()
        
        logger.warning(
            f"Revoked {revoked_count} tokens for user {user_id}"
        )
        
        return revoked_count


__all__ = ['TokenBlacklistService']

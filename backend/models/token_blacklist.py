"""
Token Blacklist model for invalidating tokens on logout.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from database import Base


class TokenBlacklist(Base):
    """
    Stores blacklisted tokens (invalidated on logout).
    Tokens are stored to prevent reuse after logout.
    """
    
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    token_hash = Column(String, unique=True, index=True)  # Hash of token to save space
    revoked_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, index=True)  # Auto-cleanup after expiration
    
    __table_args__ = (
        Index('idx_user_revoked', 'user_id', 'revoked_at'),
        Index('idx_expires', 'expires_at'),
    )


__all__ = ['TokenBlacklist']

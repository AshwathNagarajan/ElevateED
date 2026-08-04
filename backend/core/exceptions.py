"""
Custom exception classes for ElevateED.
Provides structured error handling with HTTP status codes.
"""

from typing import Any, Dict, Optional
from fastapi import status


class ElevateedException(Exception):
    """Base exception for all ElevateED application errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ElevateedException):
    """Validation error (400)"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(ElevateedException):
    """Authentication error (401)"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(ElevateedException):
    """Authorization/permission error (403)"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(ElevateedException):
    """Resource not found (404)"""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class ConflictError(ElevateedException):
    """Resource conflict (409)"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_ERROR",
            details=details
        )


class RateLimitError(ElevateedException):
    """Rate limit exceeded (429)"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_ERROR"
        )


class InternalServerError(ElevateedException):
    """Internal server error (500)"""
    
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            details=details
        )


class ServiceError(ElevateedException):
    """Service layer error"""
    
    def __init__(
        self,
        service: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(
            message=f"[{service}] {message}",
            status_code=status_code,
            error_code="SERVICE_ERROR",
            details={"service": service}
        )


class DatabaseError(ElevateedException):
    """Database operation error"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class IntegrityError(ElevateedException):
    """Database integrity constraint violation"""
    
    def __init__(
        self,
        message: str = "Data integrity violation",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="INTEGRITY_ERROR",
            details=details
        )


class ExternalServiceError(ElevateedException):
    """Error calling external service"""
    
    def __init__(
        self,
        service: str,
        message: str,
        status_code: int = status.HTTP_502_BAD_GATEWAY
    ):
        super().__init__(
            message=f"External service error: {service} - {message}",
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


__all__ = [
    'ElevateedException',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'ConflictError',
    'RateLimitError',
    'InternalServerError',
    'ServiceError',
    'DatabaseError',
    'IntegrityError',
    'ExternalServiceError'
]

"""
Standard response formatting for all API endpoints.
Ensures consistent response structure across the application.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class ErrorDetail(BaseModel):
    """Single error detail"""
    field: Optional[str] = None
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str = Field(..., description="Error type")
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Application error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    path: Optional[str] = Field(None, description="Request path")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response format"""
    success: bool = True
    data: T
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response format"""
    success: bool = True
    data: List[T]
    pagination: Dict[str, Any] = Field(
        ...,
        description="Pagination metadata"
    )
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


def success_response(
    data: Any,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standard success response.
    
    Args:
        data: Response data
        message: Optional success message
    
    Returns:
        Formatted response dictionary
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(
    error_type: str,
    status_code: int,
    message: str,
    error_code: str,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standard error response.
    
    Args:
        error_type: Type of error
        status_code: HTTP status code
        message: Error message
        error_code: Application error code
        details: Additional error details
        path: Request path
    
    Returns:
        Formatted error response dictionary
    """
    return {
        "error": error_type,
        "status_code": status_code,
        "message": message,
        "error_code": error_code,
        "details": details,
        "path": path,
        "timestamp": datetime.utcnow().isoformat()
    }


def paginated_response(
    data: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a paginated response.
    
    Args:
        data: List of items
        page: Current page number (1-indexed)
        page_size: Items per page
        total: Total number of items
        message: Optional message
    
    Returns:
        Formatted paginated response
    """
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "success": True,
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        },
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def list_response(
    data: List[Any],
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a list response.
    
    Args:
        data: List of items
        message: Optional message
    
    Returns:
        Formatted list response
    """
    return {
        "success": True,
        "data": data,
        "count": len(data),
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


__all__ = [
    'ErrorDetail',
    'ErrorResponse',
    'SuccessResponse',
    'PaginatedResponse',
    'success_response',
    'error_response',
    'paginated_response',
    'list_response'
]

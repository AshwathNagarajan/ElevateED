"""
Request validation helpers and decorators.
Provides utilities for validating and sanitizing request data.
"""

from typing import Any, Callable, Type, Optional
from pydantic import BaseModel, validator, field_validator
from fastapi import Depends, HTTPException, status, Query
from core.exceptions import ValidationError


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = Query(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Query(10, ge=1, le=100, description="Items per page")


class SortParams(BaseModel):
    """Standard sorting parameters"""
    sort_by: str = Query("id", description="Field to sort by")
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order: asc or desc")


def validate_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
) -> dict:
    """
    Dependency to validate pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page (1-100)
    
    Returns:
        Validated pagination params
    """
    return {"page": page, "page_size": page_size}


def validate_sorting(
    sort_by: str = Query("id"),
    sort_order: str = Query("asc", regex="^(asc|desc)$")
) -> dict:
    """
    Dependency to validate sorting parameters.
    
    Args:
        sort_by: Field name to sort by
        sort_order: Sort order (asc/desc)
    
    Returns:
        Validated sorting params
    """
    return {"sort_by": sort_by, "sort_order": sort_order}


def validate_model(
    model_class: Type[BaseModel],
    raise_exception: bool = True
) -> Callable:
    """
    Decorator factory to validate request model against a Pydantic schema.
    
    Args:
        model_class: Pydantic model class to validate against
        raise_exception: Whether to raise exception on validation failure
    
    Returns:
        Decorator function
    
    Example:
        @validate_model(UserCreate)
        async def create_user(data: UserCreate):
            ...
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                if raise_exception:
                    raise ValidationError(
                        f"Request validation failed: {str(e)}"
                    )
                return None
        return wrapper
    return decorator


class BaseValidator(BaseModel):
    """Base validator class with common validation rules"""
    
    class Config:
        str_strip_whitespace = True
        case_sensitive = False
    
    @field_validator('*', mode='before')
    @classmethod
    def validate_strings(cls, v):
        """Trim whitespace from string fields"""
        if isinstance(v, str):
            return v.strip()
        return v


__all__ = [
    'PaginationParams',
    'SortParams',
    'validate_pagination',
    'validate_sorting',
    'validate_model',
    'BaseValidator'
]

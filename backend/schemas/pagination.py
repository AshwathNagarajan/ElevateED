from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic, Optional

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items matching the filter")
    count: int = Field(..., description="Number of items in this response")
    page: int = Field(..., description="Current page number (1-indexed)")
    pages: int = Field(..., description="Total number of pages")
    items: List[T] = Field(..., description="List of items for this page")

    class Config:
        from_attributes = True


class PaginatedCourseResponse(BaseModel):
    """Paginated response for courses."""
    skip: int
    limit: int
    total: int = Field(..., description="Total courses matching filters")
    count: int = Field(..., description="Number of courses in this response")
    page: int = Field(..., description="Current page number (1-indexed)")
    pages: int = Field(..., description="Total number of pages")
    filters: dict = Field(..., description="Applied filters")
    items: List[dict] = Field(..., description="List of courses")

    class Config:
        from_attributes = True


class CourseFilterOptions(BaseModel):
    """Available filter options for courses."""
    track_types: List[str] = Field(..., description="Available track types")
    levels: List[str] = Field(..., description="Available course levels")

    class Config:
        from_attributes = True

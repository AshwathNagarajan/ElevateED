"""
Middleware for request/response logging, error handling, and context tracking.
"""

import uuid
import time
from typing import Callable, Coroutine, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError as SQLIntegrityError, DatabaseError as SQLDatabaseError
from pydantic import ValidationError

from core.logging import logger, ContextVar, log_request, log_error
from core.exceptions import (
    ElevateedException,
    ValidationError as ValidationErrorException,
    InternalServerError
)
from core.responses import error_response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request context (request ID, user ID, path).
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        ContextVar.set('request_id', request_id)
        ContextVar.set('path', request.url.path)
        
        # Try to extract user ID from token (optional)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            ContextVar.set('auth_token', auth_header[7:])
        
        try:
            response = await call_next(request)
            return response
        finally:
            ContextVar.clear()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = ContextVar.get('request_id', 'N/A')
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log request
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id
            )
            
            return response
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "duration_ms": duration_ms,
                    "request_id": request_id,
                    "error": str(exc)
                }
            )
            raise


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle all uncaught exceptions and return consistent error responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except ElevateedException as exc:
            # Handle custom application exceptions
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response(
                    error_type=exc.__class__.__name__,
                    status_code=exc.status_code,
                    message=exc.message,
                    error_code=exc.error_code,
                    details=exc.details,
                    path=str(request.url.path)
                )
            )
        except HTTPException as exc:
            # Handle FastAPI HTTPExceptions
            return JSONResponse(
                status_code=exc.status_code,
                content=error_response(
                    error_type="HTTPException",
                    status_code=exc.status_code,
                    message=exc.detail,
                    error_code="HTTP_ERROR",
                    path=str(request.url.path)
                )
            )
        except ValidationError as exc:
            # Handle Pydantic validation errors
            errors = [
                {
                    "field": ".".join(str(x) for x in error["loc"]),
                    "type": error["type"],
                    "message": error["msg"]
                }
                for error in exc.errors()
            ]
            
            log_error(
                "Validation error",
                context={"errors": errors}
            )
            
            return JSONResponse(
                status_code=422,
                content=error_response(
                    error_type="ValidationError",
                    status_code=422,
                    message="Request validation failed",
                    error_code="VALIDATION_ERROR",
                    details={"validation_errors": errors},
                    path=str(request.url.path)
                )
            )
        except SQLIntegrityError as exc:
            # Handle database integrity constraint violations
            log_error(
                "Database integrity error",
                error=exc
            )
            
            return JSONResponse(
                status_code=409,
                content=error_response(
                    error_type="DatabaseIntegrityError",
                    status_code=409,
                    message="Resource already exists or violates database constraints",
                    error_code="INTEGRITY_ERROR",
                    path=str(request.url.path)
                )
            )
        except SQLDatabaseError as exc:
            # Handle database errors
            log_error(
                "Database error",
                error=exc
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response(
                    error_type="DatabaseError",
                    status_code=500,
                    message="Database operation failed",
                    error_code="DATABASE_ERROR",
                    path=str(request.url.path)
                )
            )
        except Exception as exc:
            # Handle all other unexpected exceptions
            log_error(
                f"Unexpected error: {type(exc).__name__}",
                error=exc
            )
            
            return JSONResponse(
                status_code=500,
                content=error_response(
                    error_type=type(exc).__name__,
                    status_code=500,
                    message="Internal server error",
                    error_code="INTERNAL_ERROR",
                    path=str(request.url.path)
                )
            )


__all__ = [
    'RequestContextMiddleware',
    'RequestLoggingMiddleware',
    'GlobalExceptionMiddleware'
]

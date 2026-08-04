"""
Centralized logging system for ElevateED.
Provides structured logging with context tracking.
"""

import logging
import json
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from pythonjsonlogger import jsonlogger
from config import settings


class ContextVar:
    """Thread-safe context variable for storing request context"""
    _storage = {}
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        cls._storage[key] = value
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        return cls._storage.get(key, default)
    
    @classmethod
    def clear(cls) -> None:
        cls._storage.clear()


class ContextFilter(logging.Filter):
    """Filter to add context information to log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = ContextVar.get('request_id', 'N/A')
        record.user_id = ContextVar.get('user_id', 'N/A')
        record.path = ContextVar.get('path', 'N/A')
        return True


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging with JSON format and context.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("elevatedED")
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Use JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s %(user_id)s %(path)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add context filter
    context_filter = ContextFilter()
    console_handler.addFilter(context_filter)
    
    logger.addHandler(console_handler)
    
    return logger


# Create global logger instance
logger = setup_logging(
    level="DEBUG" if settings.DEBUG else "INFO"
)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log HTTP request with structured data.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: User ID (optional)
        request_id: Request ID for tracing (optional)
    """
    logger.info(
        f"{method} {path} {status_code}",
        extra={
            "http_method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def log_error(
    message: str,
    error: Optional[Exception] = None,
    context: Optional[Dict[str, Any]] = None,
    level: str = "ERROR"
) -> None:
    """
    Log error with structured context.
    
    Args:
        message: Error message
        error: Exception object (optional)
        context: Additional context data (optional)
        level: Log level
    """
    extra = context or {}
    extra["timestamp"] = datetime.utcnow().isoformat()
    
    if error:
        extra["error_type"] = type(error).__name__
        extra["error_message"] = str(error)
    
    log_func = getattr(logger, level.lower(), logger.error)
    log_func(message, extra=extra, exc_info=error)


def log_service_call(
    service_name: str,
    method_name: str,
    duration_ms: float,
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """
    Log service layer calls for debugging and monitoring.
    
    Args:
        service_name: Name of the service
        method_name: Name of the method called
        duration_ms: Execution time in milliseconds
        success: Whether the call succeeded
        error: Error message if failed
    """
    level = "INFO" if success else "ERROR"
    message = f"{service_name}.{method_name}()"
    
    extra = {
        "service": service_name,
        "method": method_name,
        "duration_ms": duration_ms,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if error:
        extra["error"] = error
    
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)


__all__ = [
    'logger',
    'setup_logging',
    'ContextVar',
    'ContextFilter',
    'log_request',
    'log_error',
    'log_service_call'
]

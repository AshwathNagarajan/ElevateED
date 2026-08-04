"""
Role-Based Access Control (RBAC) decorators and utilities.
Provides role-based authorization for routes and services.
"""

from typing import Callable, List, Optional, Coroutine, Any
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, RoleEnum
from core.exceptions import AuthorizationError, AuthenticationError
from core.logging import logger

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract and verify current authenticated user.
    Checks if token is blacklisted (invalidated by logout).
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
    
    Returns:
        Current authenticated user
    
    Raises:
        AuthenticationError: If token is invalid, expired, blacklisted, or user not found
    """
    from services.auth import verify_token  # Import here to avoid circular imports
    from services.token_blacklist_service import TokenBlacklistService
    
    try:
        token = credentials.credentials
        
        # Check if token is blacklisted first
        if TokenBlacklistService.is_blacklisted(token, db):
            logger.warning("Attempted to use blacklisted token")
            raise AuthenticationError("Token has been revoked")
        
        token_data = verify_token(token)
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise AuthenticationError("Invalid or expired token")
    
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if not user:
        raise AuthenticationError("User not found")
    
    return user


def require_role(*roles: str) -> Callable:
    """
    Decorator to require specific roles for a route.
    
    Args:
        *roles: One or more role names (e.g., 'admin', 'mentor', 'student')
    
    Returns:
        Decorator function
    
    Example:
        @router.get("/admin/users")
        @require_role('admin')
        def get_all_users(current_user: User = Depends(get_current_user)):
            ...
        
        @router.get("/dashboard")
        @require_role('admin', 'mentor', 'student')  # Any of these roles
        def get_dashboard(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_user: User = kwargs.get('current_user')
            
            if not current_user:
                raise AuthenticationError("User not authenticated")
            
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            if user_role not in roles:
                allowed_roles = ", ".join(roles)
                logger.warning(
                    f"Unauthorized access attempt: User {current_user.id} with role '{user_role}' tried to access endpoint requiring roles: {allowed_roles}"
                )
                raise AuthorizationError(
                    f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_user: User = kwargs.get('current_user')
            
            if not current_user:
                raise AuthenticationError("User not authenticated")
            
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            if user_role not in roles:
                allowed_roles = ", ".join(roles)
                logger.warning(
                    f"Unauthorized access attempt: User {current_user.id} with role '{user_role}' tried to access endpoint requiring roles: {allowed_roles}"
                )
                raise AuthorizationError(
                    f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            
            return func(*args, **kwargs)
        
        # Determine if function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin role.
    
    Example:
        @require_admin
        def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
            ...
    """
    return require_role('admin')(func)


def require_mentor(func: Callable) -> Callable:
    """
    Decorator to require mentor or admin role.
    
    Example:
        @require_mentor
        def update_student_progress(
            progress: ProgressUpdate,
            current_user: User = Depends(get_current_user)
        ):
            ...
    """
    return require_role('mentor', 'admin')(func)


def require_student(func: Callable) -> Callable:
    """
    Decorator to require student, mentor, or admin role.
    
    Example:
        @require_student
        def submit_quiz(
            submission: QuizSubmission,
            current_user: User = Depends(get_current_user)
        ):
            ...
    """
    return require_role('student', 'mentor', 'admin')(func)


def require_owner_or_admin(
    owner_id_param: str = "user_id"
) -> Callable:
    """
    Decorator to require that user is either the resource owner or admin.
    
    Args:
        owner_id_param: Name of the parameter containing the owner/resource user ID
    
    Example:
        @require_owner_or_admin('student_id')
        def get_student_progress(
            student_id: int,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_user: User = kwargs.get('current_user')
            owner_id = kwargs.get(owner_id_param)
            
            if not current_user:
                raise AuthenticationError("User not authenticated")
            
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            # Admin can access anything
            if user_role == 'admin':
                return await func(*args, **kwargs)
            
            # Check if current user owns the resource
            if str(current_user.id) != str(owner_id):
                logger.warning(
                    f"Access denied: User {current_user.id} tried to access resource owned by {owner_id}"
                )
                raise AuthorizationError("You can only access your own resources")
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_user: User = kwargs.get('current_user')
            owner_id = kwargs.get(owner_id_param)
            
            if not current_user:
                raise AuthenticationError("User not authenticated")
            
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
            
            # Admin can access anything
            if user_role == 'admin':
                return func(*args, **kwargs)
            
            # Check if current user owns the resource
            if str(current_user.id) != str(owner_id):
                logger.warning(
                    f"Access denied: User {current_user.id} tried to access resource owned by {owner_id}"
                )
                raise AuthorizationError("You can only access your own resources")
            
            return func(*args, **kwargs)
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


__all__ = [
    'get_current_user',
    'require_role',
    'require_admin',
    'require_mentor',
    'require_student',
    'require_owner_or_admin',
    'security'
]

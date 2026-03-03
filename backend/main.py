from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, DatabaseError, IntegrityError
from config import settings
from database import init_db
from routes import student_router, auth_router, predict_router, skill_router, attendance_router, course_router, enrollment_router, lesson_router, quiz_router, recommendation_router, analytics_router
import logging
from typing import Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database tables
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Exception Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions (4xx and 5xx status codes).
    """
    logger.warning(f"HTTP Exception - Status: {exc.status_code}, Detail: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "status_code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors.
    """
    logger.warning(f"Validation Error - {exc.error_count()} error(s)")
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "type": error["type"],
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "ValidationError",
                "status_code": 422,
                "message": "Validation failed",
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity constraint violations.
    """
    logger.error(f"Database Integrity Error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "type": "IntegrityError",
                "status_code": 409,
                "message": "Database constraint violation - duplicate or invalid data",
                "detail": "This resource may already exist or violates a database constraint",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """
    Handle general database errors.
    """
    logger.error(f"Database Error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "DatabaseError",
                "status_code": 500,
                "message": "A database error occurred",
                "detail": "The server encountered an error accessing the database. Please try again later.",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle all other SQLAlchemy errors.
    """
    logger.error(f"SQLAlchemy Error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "DatabaseError",
                "status_code": 500,
                "message": "A database error occurred",
                "detail": "The server encountered an error with the database operation. Please try again later.",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Fallback handler for any unhandled exceptions.
    """
    logger.error(f"Unhandled Exception: {type(exc).__name__} - {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "status_code": 500,
                "message": "An unexpected error occurred",
                "detail": "The server encountered an unexpected error. Please try again later.",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        }
    )


# ==================== Routes ====================

# Include routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(predict_router)
app.include_router(skill_router)
app.include_router(attendance_router)
app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(lesson_router)
app.include_router(quiz_router)
app.include_router(recommendation_router)
app.include_router(analytics_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to ElevateED API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

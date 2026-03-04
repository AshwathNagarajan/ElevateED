from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models.user import User, RoleEnum
from models.student import Student
from schemas.auth import UserCreate, UserResponse, UserLogin, TokenResponse
from services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    require_role
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

security = HTTPBearer()

# ============================================================================
# Authentication Dependencies (must be defined before routes that use them)
# ============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_mentor(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require mentor role"""
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_value not in ["mentor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mentor access required"
        )
    return current_user


def get_student_for_user(db: Session, user: User) -> Student:
    """Get the Student record for a User, creating one if needed"""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        # Auto-create student record if missing
        student = Student(
            user_id=user.id,
            name=user.full_name,
            age=0,
            guardian_contact="",
            interest_track=None
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    return student


# ============================================================================
# Auth Routes
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Auto-create Student record for student role users
    role_value = db_user.role.value if hasattr(db_user.role, 'value') else str(db_user.role)
    if role_value == "student":
        student = Student(
            user_id=db_user.id,
            name=db_user.full_name,
            age=0,
            guardian_contact="",
            interest_track=None
        )
        db.add(student)
        db.commit()
    
    return db_user

@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token - convert role enum to string value, sub must be string
    role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role_str}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user's information"""
    return current_user

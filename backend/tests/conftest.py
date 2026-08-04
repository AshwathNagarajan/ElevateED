"""
Pytest configuration and shared fixtures for testing.

This module sets up:
- Test database (SQLite in-memory)
- FastAPI test client
- Test user fixtures (student, mentor, admin)
- Dependency override fixtures for database access
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database import Base, get_db
from models.user import User, RoleEnum
from models.student import Student
from models.mentor import Mentor
from services.auth import hash_password, create_access_token


# ============================================================================
# Test Database Configuration
# ============================================================================

# Use SQLite in-memory database for tests (fast, isolated)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_db():
    """Create and configure test database with all tables."""
    # Create engine for in-memory SQLite
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal()
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(test_db: Session):
    """Alias for tests that use the shorter db fixture name."""
    return test_db


# ============================================================================
# FastAPI Test Client
# ============================================================================

@pytest.fixture
def client(test_db: Session):
    """Create FastAPI test client with test database override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # Keep session open during test
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()


# ============================================================================
# Test User Fixtures
# ============================================================================

@pytest.fixture
def admin_user(test_db: Session) -> User:
    """Create and return an admin user for testing."""
    user = User(
        email="admin@test.com",
        full_name="Admin User",
        hashed_password=hash_password("adminpass123"),
        role=RoleEnum.admin
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def mentor_user(test_db: Session) -> User:
    """Create and return a mentor user for testing."""
    user = User(
        email="mentor@test.com",
        full_name="Mentor User",
        hashed_password=hash_password("mentorpass123"),
        role=RoleEnum.mentor
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def student_user(test_db: Session) -> User:
    """Create and return a student user for testing."""
    user = User(
        email="student@test.com",
        full_name="Student User",
        hashed_password=hash_password("studentpass123"),
        role=RoleEnum.student
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create associated student record
    student = Student(
        user_id=user.id,
        name="Student User",
        age=18,
        guardian_contact="parent@test.com",
        interest_track="AI & ML"
    )
    test_db.add(student)
    test_db.commit()
    
    return user


@pytest.fixture
def mentor_with_record(test_db: Session, mentor_user: User) -> User:
    """Create a mentor with associated mentor record."""
    mentor = Mentor(
        user_id=mentor_user.id,
        name=mentor_user.full_name,
        qualification="M.Tech",
        specialization="Python, AI, Machine Learning",
        experience_years=5,
    )
    test_db.add(mentor)
    test_db.commit()
    return mentor_user


# ============================================================================
# Authentication Token Fixtures
# ============================================================================

@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate JWT token for admin user."""
    return create_access_token(
        data={"sub": str(admin_user.id), "role": admin_user.role.value}
    )


@pytest.fixture
def mentor_token(mentor_user: User) -> str:
    """Generate JWT token for mentor user."""
    return create_access_token(
        data={"sub": str(mentor_user.id), "role": mentor_user.role.value}
    )


@pytest.fixture
def student_token(student_user: User) -> str:
    """Generate JWT token for student user."""
    return create_access_token(
        data={"sub": str(student_user.id), "role": student_user.role.value}
    )


# ============================================================================
# Helper Fixtures
# ============================================================================

def get_auth_header(token: str) -> dict:
    """Create authorization header from token."""
    return {"Authorization": f"Bearer {token}"}

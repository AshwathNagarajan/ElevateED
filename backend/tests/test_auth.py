"""
Tests for authentication endpoints.

Coverage:
- POST /auth/login - successful login, invalid email, invalid password
- GET /auth/me - authenticated user info, unauthorized access
"""

import pytest
from fastapi.testclient import TestClient


class TestLogin:
    """Test suite for login endpoint."""
    
    def test_login_successful_admin(self, client: TestClient, admin_user):
        """Test successful login with admin credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "admin@test.com",
                "password": "adminpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_successful_student(self, client: TestClient, student_user):
        """Test successful login with student credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "student@test.com",
                "password": "studentpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_successful_mentor(self, client: TestClient, mentor_user):
        """Test successful login with mentor credentials."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "mentor@test.com",
                "password": "mentorpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client: TestClient, admin_user):
        """Test login with incorrect password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "admin@test.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_missing_email(self, client: TestClient):
        """Test login with missing email field."""
        response = client.post(
            "/api/auth/login",
            json={"password": "password123"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_password(self, client: TestClient):
        """Test login with missing password field."""
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com"}
        )
        
        assert response.status_code == 422  # Validation error


class TestGetCurrentUser:
    """Test suite for GET /auth/me endpoint."""
    
    def test_get_current_user_success(self, client: TestClient, admin_token: str):
        """Test retrieving current user info with valid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["full_name"] == "Admin User"
        assert data["role"] == "admin"
        assert data["id"] > 0
    
    def test_get_current_user_student(self, client: TestClient, student_token: str):
        """Test retrieving student user info."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "student@test.com"
        assert data["role"] == "student"
    
    def test_get_current_user_mentor(self, client: TestClient, mentor_token: str):
        """Test retrieving mentor user info."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {mentor_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "mentor@test.com"
        assert data["role"] == "mentor"
    
    def test_get_current_user_no_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]
    
    def test_get_current_user_expired_token(self, client: TestClient):
        """Test accessing with an expired token (if implementation tracks expiry)."""
        # This creates an expired token (timedelta in the past)
        from datetime import timedelta
        from services.auth import create_access_token
        
        expired_token = create_access_token(
            data={"sub": "1", "role": "student"},
            expires_delta=timedelta(seconds=-1)  # Expired 1 second ago
        )
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Should reject expired token
        assert response.status_code == 401
    
    def test_get_current_user_malformed_header(self, client: TestClient):
        """Test with malformed Authorization header."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormatToken"}
        )
        
        assert response.status_code == 403

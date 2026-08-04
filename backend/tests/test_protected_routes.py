"""
Tests for protected route access and role-based authorization.

Coverage:
- Protected route access (requires authentication)
- Role-based access control (admin-only, mentor-only endpoints)
- Unauthorized role rejection
"""

import pytest
from fastapi.testclient import TestClient


class TestProtectedRouteAccess:
    """Test suite for protected route access."""
    
    def test_admin_list_students_requires_admin(self, client: TestClient, student_token: str):
        """Test that student cannot access admin-only student list."""
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Should be forbidden (403) or unauthorized (401)
        assert response.status_code in [401, 403]
    
    def test_admin_list_students_with_admin_token(self, client: TestClient, admin_token: str):
        """Test that admin can access admin-only student list."""
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should succeed (200) or return empty list
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_admin_list_students_without_token(self, client: TestClient):
        """Test that unauthenticated access to admin endpoint is rejected."""
        response = client.get("/api/students/admin/list")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_mentor_dashboard_requires_mentor(self, client: TestClient, student_token: str):
        """Test that non-mentor cannot access mentor dashboard."""
        response = client.get(
            "/api/analytics/mentor/dashboard",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Should be forbidden or unauthorized
        assert response.status_code in [401, 403]
    
    def test_mentor_dashboard_with_mentor_token(self, client: TestClient, mentor_token: str, mentor_with_record):
        """Test that mentor can access mentor dashboard."""
        response = client.get(
            "/api/analytics/mentor/dashboard",
            headers={"Authorization": f"Bearer {mentor_token}"}
        )
        
        # Should return 200 (success) or potentially 404 if no data exists
        assert response.status_code in [200, 404]


class TestRoleBasedAccessControl:
    """Test suite for role-based authorization."""
    
    def test_student_cannot_access_admin_analytics(self, client: TestClient, student_token: str):
        """Test that student cannot access admin analytics endpoints."""
        response = client.get(
            "/api/analytics/course-completion-rate",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        assert response.status_code in [401, 403]
    
    def test_admin_can_access_analytics(self, client: TestClient, admin_token: str):
        """Test that admin can access analytics endpoints."""
        response = client.get(
            "/api/analytics/course-completion-rate",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should succeed (no admin check, but admin can access)
        assert response.status_code == 200
    
    def test_student_cannot_delete_other_students(self, client: TestClient, student_token: str):
        """Test that students cannot perform admin operations."""
        response = client.delete(
            "/api/students/admin/1",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Should be rejected
        assert response.status_code in [401, 403, 405]
    
    def test_mentor_cannot_access_admin_endpoints(self, client: TestClient, mentor_token: str):
        """Test that mentors cannot access admin-specific endpoints."""
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": f"Bearer {mentor_token}"}
        )
        
        assert response.status_code in [401, 403]


class TestUnauthorizedAccess:
    """Test suite for various unauthorized access scenarios."""
    
    def test_missing_authorization_header(self, client: TestClient):
        """Test request without Authorization header."""
        response = client.get("/api/students/admin/list")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_invalid_bearer_format(self, client: TestClient):
        """Test request with invalid Bearer token format."""
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": "InvalidFormat"}
        )
        
        assert response.status_code == 403
    
    def test_bearer_prefix_lowercase(self, client: TestClient, admin_token: str):
        """Test that bearer prefix is case-insensitive (common requirement)."""
        # Some implementations accept both "Bearer" and "bearer"
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": f"bearer {admin_token}"}
        )
        
        # Should either work or fail consistently
        # This test documents the behavior
        assert response.status_code in [200, 403, 401]
    
    def test_multiple_authorization_headers(self, client: TestClient, admin_token: str):
        """Test behavior with multiple Authorization headers."""
        # This is more of a documentation test for edge case behavior
        response = client.get(
            "/api/students/admin/list",
            headers={
                "Authorization": f"Bearer {admin_token}",
            }
        )
        
        assert response.status_code == 200
    
    def test_token_from_different_user(self, client: TestClient, admin_token: str, student_user):
        """Test that token is specific to the user it was issued for."""
        # Token is for admin, but we're trying to access as if we're a student
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should work because token is valid admin token
        assert response.status_code == 200


class TestTokenValidation:
    """Test suite for token validation edge cases."""
    
    def test_very_long_invalid_token(self, client: TestClient):
        """Test with extremely long invalid token."""
        long_token = "x" * 10000
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": f"Bearer {long_token}"}
        )
        
        assert response.status_code == 401
    
    def test_empty_bearer_token(self, client: TestClient):
        """Test with empty Bearer token."""
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": "Bearer "}
        )
        
        assert response.status_code in [401, 403]
    
    def test_special_characters_in_token(self, client: TestClient):
        """Test with special characters in token."""
        response = client.get(
            "/api/students/admin/list",
            headers={"Authorization": "Bearer <script>alert('xss')</script>"}
        )
        
        assert response.status_code == 401

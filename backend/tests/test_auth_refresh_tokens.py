"""
Tests for JWT Refresh Token and Logout functionality (Phase 2 Task 1).
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status
from sqlalchemy.orm import Session
from jose import jwt

from models.user import User, RoleEnum
from models.token_blacklist import TokenBlacklist
from schemas.auth import TokenPairResponse
from core.security import TokenManager
from services.token_blacklist_service import TokenBlacklistService
from config import settings


@pytest.fixture
def test_user(db: Session):
    """Create a test user"""
    from services.auth import hash_password
    
    user = User(
        email="testuser@example.com",
        full_name="Test User",
        hashed_password=hash_password("password123"),
        role=RoleEnum.student
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestLoginWithTokenPair:
    """Test /auth/login returns access and refresh tokens"""
    
    def test_login_returns_token_pair(self, client, test_user):
        """Login should return both access and refresh tokens"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in_minutes"] == 15
        
        # Verify access token is valid
        access_payload = TokenManager.verify_token(
            data["access_token"],
            token_type="access"
        )
        assert int(access_payload["sub"]) == test_user.id
        assert access_payload["role"] == "student"
        
        # Verify refresh token is valid
        refresh_payload = TokenManager.verify_token(
            data["refresh_token"],
            token_type="refresh"
        )
        assert int(refresh_payload["sub"]) == test_user.id
    
    def test_login_invalid_credentials(self, client, test_user):
        """Login with invalid credentials should fail"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Login with nonexistent email should fail"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshTokenEndpoint:
    """Test /auth/refresh endpoint"""
    
    def test_refresh_returns_new_token_pair(self, client, db: Session, test_user):
        """Refresh endpoint should return new access and refresh tokens"""
        # Create initial tokens
        access_token = TokenManager.create_access_token(test_user.id, "student")
        refresh_token = TokenManager.create_refresh_token(test_user.id)
        
        # Call refresh endpoint
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in_minutes"] == 15
        
        # New tokens should be different from originals
        assert data["access_token"] != access_token
        assert data["refresh_token"] != refresh_token
        
        # Verify new tokens are valid
        new_access_payload = TokenManager.verify_token(
            data["access_token"],
            token_type="access"
        )
        assert int(new_access_payload["sub"]) == test_user.id
    
    def test_refresh_with_invalid_token(self, client):
        """Refresh with invalid token should fail"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_with_access_token_fails(self, client, test_user):
        """Refresh with access token instead of refresh token should fail"""
        # Create access token (not refresh token)
        access_token = TokenManager.create_access_token(test_user.id, "student")
        
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": access_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_with_expired_token(self, client, test_user, db: Session):
        """Refresh with expired token should fail"""
        # Create expired token
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {
            "sub": str(test_user.id),
            "role": "student",
            "type": "refresh",
            "exp": past_time
        }
        expired_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": expired_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_with_blacklisted_token(self, client, db: Session, test_user):
        """Refresh with blacklisted refresh token should fail"""
        # Create refresh token
        refresh_token = TokenManager.create_refresh_token(test_user.id)
        
        # Blacklist it
        payload = TokenManager.verify_token(refresh_token, token_type="refresh")
        expires_at = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        TokenBlacklistService.add_to_blacklist(
            refresh_token,
            test_user.id,
            expires_at,
            db
        )
        
        # Try to use blacklisted token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogoutEndpoint:
    """Test /auth/logout endpoint"""
    
    def test_logout_blacklists_token(self, client, db: Session, test_user):
        """Logout should add token to blacklist"""
        # Create token
        access_token = TokenManager.create_access_token(test_user.id, "student")
        
        # Call logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        
        # Verify token is now blacklisted
        assert TokenBlacklistService.is_blacklisted(access_token, db) is True
    
    def test_logout_without_token_fails(self, client):
        """Logout without token should fail"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_logout_with_invalid_token_fails(self, client):
        """Logout with invalid token should fail"""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_cannot_use_token_after_logout(self, client, db: Session, test_user):
        """Using a token after logout should fail"""
        # Create and logout with token
        access_token = TokenManager.create_access_token(test_user.id, "student")
        
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert logout_response.status_code == status.HTTP_200_OK
        
        # Try to use token after logout
        auth_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert auth_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_cannot_logout_twice(self, client, db: Session, test_user):
        """Logging out twice with same token should fail second time"""
        access_token = TokenManager.create_access_token(test_user.id, "student")
        
        # First logout
        response1 = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second logout should fail
        response2 = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response2.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenBlacklistService:
    """Test TokenBlacklistService functionality"""
    
    def test_add_and_check_blacklist(self, db: Session, test_user):
        """Test adding and checking tokens in blacklist"""
        token = "test_token_123"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Should not be blacklisted initially
        assert TokenBlacklistService.is_blacklisted(token, db) is False
        
        # Add to blacklist
        TokenBlacklistService.add_to_blacklist(token, test_user.id, expires_at, db)
        
        # Should now be blacklisted
        assert TokenBlacklistService.is_blacklisted(token, db) is True
    
    def test_cannot_add_duplicate_to_blacklist(self, db: Session, test_user):
        """Adding same token twice should only create one entry"""
        token = "test_token_123"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        # Add twice
        TokenBlacklistService.add_to_blacklist(token, test_user.id, expires_at, db)
        TokenBlacklistService.add_to_blacklist(token, test_user.id, expires_at, db)
        
        # Should only have one entry
        count = db.query(TokenBlacklist).filter(
            TokenBlacklist.user_id == test_user.id
        ).count()
        assert count == 1
    
    def test_cleanup_expired_tokens(self, db: Session, test_user):
        """Cleanup should remove expired tokens"""
        # Add expired token
        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        expired_entry = TokenBlacklist(
            user_id=test_user.id,
            token_hash="expired_token_hash",
            expires_at=expired_time
        )
        db.add(expired_entry)
        db.commit()
        
        # Add valid token
        valid_time = datetime.now(timezone.utc) + timedelta(hours=1)
        valid_entry = TokenBlacklist(
            user_id=test_user.id,
            token_hash="valid_token_hash",
            expires_at=valid_time
        )
        db.add(valid_entry)
        db.commit()
        
        # Cleanup
        removed = TokenBlacklistService.cleanup_expired(db)
        
        assert removed >= 1  # At least the expired token
        
        # Expired should be gone, valid should remain
        assert TokenBlacklistService.is_blacklisted("test_token_123", db) is False


class TestTokenSecurity:
    """Test token security aspects"""
    
    def test_token_expiration_times(self, test_user):
        """Test that tokens have correct expiration times"""
        access_token = TokenManager.create_access_token(test_user.id, "student")
        refresh_token = TokenManager.create_refresh_token(test_user.id)
        
        access_payload = TokenManager.verify_token(access_token, token_type="access")
        refresh_payload = TokenManager.verify_token(refresh_token, token_type="refresh")
        
        now = datetime.now(timezone.utc).timestamp()
        
        # Access token should expire in ~15 minutes
        access_exp = access_payload["exp"]
        access_delta = (access_exp - now) / 60  # minutes
        assert 14 <= access_delta <= 16
        
        # Refresh token should expire in ~7 days
        refresh_exp = refresh_payload["exp"]
        refresh_delta = (refresh_exp - now) / 86400  # days
        assert 6.9 <= refresh_delta <= 7.1
    
    def test_token_contains_correct_claims(self, test_user):
        """Test that tokens contain required claims"""
        access_token = TokenManager.create_access_token(test_user.id, "mentor")
        
        payload = TokenManager.verify_token(access_token, token_type="access")
        
        assert payload["sub"] == str(test_user.id)
        assert payload["role"] == "mentor"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

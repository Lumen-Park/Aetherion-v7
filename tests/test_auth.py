import pytest
import os
from unittest.mock import patch
from core.auth import AuthManager


class TestAuthManager:
    def test_auth_disabled_by_default(self):
        manager = AuthManager()
        assert manager.auth_enabled is False
        auth_info = manager.authenticate("any_token")
        assert auth_info == {"role": "admin", "auth_disabled": True}
        assert manager.authorize(auth_info, "operator") is True

    def test_auth_enabled_without_token_fails(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        manager = AuthManager()
        assert manager.authenticate(None) is None
        assert manager.authenticate("") is None

    def test_api_key_authentication_success(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_API_KEYS", "test-key-123:admin,other-key:operator")
        manager = AuthManager()
        auth_info = manager.authenticate("test-key-123")
        assert auth_info is not None
        assert auth_info["role"] == "admin"

    def test_api_key_authentication_failure(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_API_KEYS", "valid:admin")
        manager = AuthManager()
        assert manager.authenticate("wrong-key") is None

    def test_authorization_admin_can_do_anything(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        manager = AuthManager()
        auth_info = {"role": "admin"}
        assert manager.authorize(auth_info, "admin") is True
        assert manager.authorize(auth_info, "operator") is True
        assert manager.authorize(auth_info, "viewer") is True

    def test_authorization_operator_limited(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        manager = AuthManager()
        auth_info = {"role": "operator"}
        assert manager.authorize(auth_info, "admin") is False
        assert manager.authorize(auth_info, "operator") is True
        assert manager.authorize(auth_info, "viewer") is True

    def test_authorization_viewer_limited(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        manager = AuthManager()
        auth_info = {"role": "viewer"}
        assert manager.authorize(auth_info, "admin") is False
        assert manager.authorize(auth_info, "operator") is False
        assert manager.authorize(auth_info, "viewer") is True

    def test_generate_api_key(self):
        key1 = AuthManager.generate_api_key()
        key2 = AuthManager.generate_api_key()
        assert len(key1) == 43  # 32 bytes base64 encoded
        assert key1 != key2

    def test_generate_jwt(self):
        token = AuthManager.generate_jwt("user123", "operator", "secret", expires_in_hours=1)
        assert token is not None
        # Verify it can be decoded
        manager = AuthManager()
        manager.jwt_secret = "secret"
        payload = manager.verify_jwt(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "operator"

    def test_verify_jwt_invalid(self):
        manager = AuthManager()
        manager.jwt_secret = "secret"
        assert manager.verify_jwt("invalid.token.here") is None
        assert manager.verify_jwt("") is None

    def test_authenticate_with_jwt(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_JWT_SECRET", "jwt-secret")
        manager = AuthManager()
        token = AuthManager.generate_jwt("user", "operator", "jwt-secret")
        auth_info = manager.authenticate(token)
        assert auth_info is not None
        assert auth_info["role"] == "operator"

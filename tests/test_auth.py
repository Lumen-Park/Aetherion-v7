import os
from unittest.mock import patch

import pytest

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
        monkeypatch.setenv(
            "AETHERION_API_KEYS", "test-key-123:admin,other-key:operator"
        )
        manager = AuthManager()
        auth_info = manager.authenticate("test-key-123")
        assert auth_info is not None
        assert auth_info["role"] == "admin"

    def test_api_key_authentication_failure(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_API_KEYS", "valid:admin")
        manager = AuthManager()
        assert manager.authenticate("wrong-key") is None

    def test_api_key_empty_string(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_API_KEYS", "key1:admin")
        manager = AuthManager()
        assert manager.authenticate("") is None

    def test_verify_api_key_none(self):
        manager = AuthManager()
        assert manager.verify_api_key(None) is None

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

    def test_authorize_unknown_role_defaults_to_viewer(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        manager = AuthManager()
        auth_info = {"role": "unknown"}
        assert manager.authorize(auth_info, "admin") is False
        assert manager.authorize(auth_info, "operator") is False
        assert manager.authorize(auth_info, "viewer") is False

    def test_generate_api_key(self):
        key1 = AuthManager.generate_api_key()
        key2 = AuthManager.generate_api_key()
        assert len(key1) == 43
        assert key1 != key2

    def test_generate_jwt(self):
        secret = "a-very-long-secret-key-that-is-at-least-32-bytes-long!!"
        token = AuthManager.generate_jwt(
            "user123", "operator", secret, expires_in_hours=1
        )
        assert token is not None
        manager = AuthManager()
        manager.jwt_secret = secret
        payload = manager.verify_jwt(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "operator"

    def test_verify_jwt_invalid(self):
        manager = AuthManager()
        manager.jwt_secret = (
            "a-very-long-secret-key-that-is-at-least-32-bytes-long!!"
        )
        assert manager.verify_jwt("invalid.token.here") is None
        assert manager.verify_jwt("") is None

    def test_verify_jwt_no_secret(self):
        manager = AuthManager()
        manager.jwt_secret = ""
        assert manager.verify_jwt("some.token") is None

    def test_authenticate_with_jwt(self, monkeypatch):
        secret = "a-very-long-secret-key-that-is-at-least-32-bytes-long!!"
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_JWT_SECRET", secret)
        manager = AuthManager()
        token = AuthManager.generate_jwt("user", "operator", secret)
        auth_info = manager.authenticate(token)
        assert auth_info is not None
        assert auth_info["role"] == "operator"

    def test_authenticate_api_key_first_then_jwt(self, monkeypatch):
        secret = "a-very-long-secret-key-that-is-at-least-32-bytes-long!!"
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        monkeypatch.setenv("AETHERION_API_KEYS", "api-key:admin")
        monkeypatch.setenv("AETHERION_JWT_SECRET", secret)
        manager = AuthManager()
        assert manager.authenticate("api-key")["role"] == "admin"
        token = AuthManager.generate_jwt("user", "operator", secret)
        assert manager.authenticate(token)["role"] == "operator"

    def test_load_api_keys_malformed_entry_ignored(self, monkeypatch):
        monkeypatch.setenv(
            "AETHERION_API_KEYS", "valid:admin,badentry,another:operator"
        )
        manager = AuthManager()
        assert len(manager.api_keys) == 2

    def test_load_api_keys_empty_string(self, monkeypatch):
        monkeypatch.setenv("AETHERION_API_KEYS", "")
        manager = AuthManager()
        assert manager.api_keys == {}

    def test_jwt_not_available_fallback(self, monkeypatch):
        monkeypatch.setenv("AETHERION_JWT_SECRET", "secret")
        import core.auth

        monkeypatch.setattr(core.auth, "JWT_AVAILABLE", False)
        manager = AuthManager()
        assert manager.verify_jwt("any.token") is None
        with pytest.raises(ImportError):
            AuthManager.generate_jwt("user", "role", "secret")

    def test_authenticate_with_oauth_token(self, monkeypatch):
        monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
        manager = AuthManager()
        with patch("core.oauth.OAuthManager.get_user_info") as mock_get_info:
            mock_get_info.return_value = {
                "sub": "12345",
                "email": "user@example.com",
                "name": "Test User",
            }
            auth_info = manager.authenticate("oauth2:google:fake-access-token")
            assert auth_info is not None
            assert auth_info["email"] == "user@example.com"
            assert auth_info["role"] == "operator"

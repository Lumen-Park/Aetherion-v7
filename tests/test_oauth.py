from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest

from core.oauth import OAuthManager, OIDCProvider


class TestOIDCProvider:
    def test_provider_creation(self):
        provider = OIDCProvider(
            name="test",
            client_id="id",
            client_secret="secret",
            authorization_endpoint="https://auth.example.com",
            token_endpoint="https://token.example.com",
            userinfo_endpoint="https://userinfo.example.com",
        )
        assert provider.name == "test"
        assert provider.client_id == "id"
        assert provider.scopes == ["openid", "email", "profile"]

    def test_create_google_provider(self):
        provider = OAuthManager.create_google_provider(
            "google-id", "google-secret"
        )
        assert provider.name == "google"
        assert "accounts.google.com" in provider.authorization_endpoint
        assert "openid" in provider.scopes

    def test_create_github_provider(self):
        provider = OAuthManager.create_github_provider(
            "github-id", "github-secret"
        )
        assert provider.name == "github"
        assert urlparse(provider.authorization_endpoint).hostname == "github.com"
        assert "user:email" in provider.scopes


class TestOAuthManager:
    def test_init_loads_providers_from_env(self, monkeypatch):
        monkeypatch.setenv("AETHERION_OAUTH_PROVIDERS", "google,github")
        monkeypatch.setenv("AETHERION_OAUTH_GOOGLE_CLIENT_ID", "g-id")
        monkeypatch.setenv("AETHERION_OAUTH_GOOGLE_CLIENT_SECRET", "g-secret")
        monkeypatch.setenv("AETHERION_OAUTH_GITHUB_CLIENT_ID", "gh-id")
        monkeypatch.setenv("AETHERION_OAUTH_GITHUB_CLIENT_SECRET", "gh-secret")

        manager = OAuthManager()
        assert "google" in manager.providers
        assert "github" in manager.providers

    def test_register_provider(self):
        manager = OAuthManager()
        provider = OIDCProvider(
            name="custom",
            client_id="id",
            client_secret="secret",
            authorization_endpoint="https://auth.example.com",
            token_endpoint="https://token.example.com",
            userinfo_endpoint="https://userinfo.example.com",
        )
        manager.register_provider(provider)
        assert "custom" in manager.providers

    def test_get_authorization_url_unknown_provider(self):
        manager = OAuthManager()
        with pytest.raises(ValueError, match="Unknown provider"):
            manager.get_authorization_url("nonexistent")

    def test_get_authorization_url_success(self, monkeypatch):
        monkeypatch.setenv("AETHERION_OAUTH_PROVIDERS", "test")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_ID", "id")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_SECRET", "secret")
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_AUTH_ENDPOINT", "https://auth.test.com"
        )
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_TOKEN_ENDPOINT", "https://token.test.com"
        )
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_USERINFO_ENDPOINT",
            "https://userinfo.test.com",
        )

        manager = OAuthManager()
        url = manager.get_authorization_url("test", state="mystate")
        # The URL returned by OAuth2Client is the redirect URI with parameters,
        # not the remote authorization endpoint. So we check for expected parameters.
        assert "response_type=code" in url
        assert "client_id=id" in url
        assert "state=mystate" in url
        assert "code_challenge_method=S256" in url
        assert "code_challenge=" in url
        assert manager._temp_code_verifier is not None
        assert manager._temp_state == "mystate"

    def test_exchange_code_for_token_success(self, monkeypatch):
        monkeypatch.setenv("AETHERION_OAUTH_PROVIDERS", "test")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_ID", "id")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_SECRET", "secret")
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_AUTH_ENDPOINT", "https://auth.test.com"
        )
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_TOKEN_ENDPOINT", "https://token.test.com"
        )
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_USERINFO_ENDPOINT",
            "https://userinfo.test.com",
        )

        manager = OAuthManager()
        manager._temp_code_verifier = "verifier"
        manager._temp_state = "state"

        with patch("core.oauth.OAuth2Client") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            mock_client.fetch_token.return_value = {
                "access_token": "fake-token"
            }

            token = manager.exchange_code_for_token(
                "test", "auth-code", state="state"
            )
            assert token["access_token"] == "fake-token"

    def test_exchange_code_for_token_state_mismatch(self, monkeypatch):
        monkeypatch.setenv("AETHERION_OAUTH_PROVIDERS", "test")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_ID", "id")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_SECRET", "secret")
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_TOKEN_ENDPOINT", "https://token.test.com"
        )

        manager = OAuthManager()
        manager._temp_state = "correct-state"
        with pytest.raises(ValueError, match="State mismatch"):
            manager.exchange_code_for_token(
                "test", "code", state="wrong-state"
            )

    def test_get_user_info_success(self, monkeypatch):
        monkeypatch.setenv("AETHERION_OAUTH_PROVIDERS", "test")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_ID", "id")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_SECRET", "secret")
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_USERINFO_ENDPOINT",
            "https://userinfo.test.com",
        )

        manager = OAuthManager()
        with patch("core.oauth.httpx.Client") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value.__enter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.json.return_value = {"email": "user@example.com"}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response

            user_info = manager.get_user_info("test", "token")
            assert user_info["email"] == "user@example.com"

    def test_verify_id_token(self, monkeypatch):
        monkeypatch.setenv("AETHERION_OAUTH_PROVIDERS", "test")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_ID", "id")
        monkeypatch.setenv("AETHERION_OAUTH_TEST_CLIENT_SECRET", "secret")
        monkeypatch.setenv(
            "AETHERION_OAUTH_TEST_USERINFO_ENDPOINT",
            "https://userinfo.test.com",
        )

        manager = OAuthManager()
        with patch("core.oauth.jwt") as mock_jwt:
            mock_jwt.decode.return_value = {"sub": "123"}
            payload = manager.verify_id_token("test", "fake-id-token")
            assert payload["sub"] == "123"

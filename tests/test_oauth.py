def test_authenticate_with_oauth_token(self, monkeypatch):
    monkeypatch.setenv("AETHERION_REQUIRE_AUTH", "true")
    from core.auth import AuthManager

    manager = AuthManager()

    # Mock OAuthManager.get_user_info
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

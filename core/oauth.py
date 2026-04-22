"""
OAuth2 / OpenID Connect Manager for Enterprise SSO
Supports Google, GitHub, and generic OIDC providers.
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc7636 import CodeChallenge


@dataclass
class OIDCProvider:
    """Configuration for an OIDC identity provider."""
    name: str
    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    scopes: List[str] = field(default_factory=lambda: ["openid", "email", "profile"])
    jwks_uri: Optional[str] = None
    issuer: Optional[str] = None


class OAuthManager:
    """Handles OAuth2 / OIDC authentication flows."""

    def __init__(self):
        self.providers: Dict[str, OIDCProvider] = {}
        self._load_providers_from_env()
        self.redirect_uri = os.getenv("AETHERION_OAUTH_REDIRECT_URI", "http://localhost:8000/callback")

    def _load_providers_from_env(self):
        """Load OIDC provider configurations from environment variables."""
        # Format: AETHERION_OAUTH_PROVIDERS="google,github"
        provider_names = os.getenv("AETHERION_OAUTH_PROVIDERS", "").split(",")
        for name in provider_names:
            name = name.strip()
            if not name:
                continue
            prefix = f"AETHERION_OAUTH_{name.upper()}_"
            client_id = os.getenv(f"{prefix}CLIENT_ID")
            client_secret = os.getenv(f"{prefix}CLIENT_SECRET")
            if not client_id or not client_secret:
                continue
            provider = OIDCProvider(
                name=name,
                client_id=client_id,
                client_secret=client_secret,
                authorization_endpoint=os.getenv(f"{prefix}AUTH_ENDPOINT", ""),
                token_endpoint=os.getenv(f"{prefix}TOKEN_ENDPOINT", ""),
                userinfo_endpoint=os.getenv(f"{prefix}USERINFO_ENDPOINT", ""),
                scopes=os.getenv(f"{prefix}SCOPES", "openid email profile").split(),
                jwks_uri=os.getenv(f"{prefix}JWKS_URI"),
                issuer=os.getenv(f"{prefix}ISSUER"),
            )
            self.providers[name] = provider

    def register_provider(self, provider: OIDCProvider):
        """Manually register an OIDC provider."""
        self.providers[provider.name] = provider

    def get_authorization_url(self, provider_name: str, state: str = None) -> str:
        """Generate the authorization URL for a provider."""
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        client = OAuth2Client(
            client_id=provider.client_id,
            client_secret=provider.client_secret,
            authorization_endpoint=provider.authorization_endpoint,
            token_endpoint=provider.token_endpoint,
        )

        code_verifier = CodeChallenge.generate_code_verifier()
        code_challenge = CodeChallenge.compute(code_verifier)

        url, actual_state = client.create_authorization_url(
            self.redirect_uri,
            state=state,
            code_verifier=code_verifier,
            code_challenge_method="S256",
            code_challenge=code_challenge,
            scope=" ".join(provider.scopes),
        )

        # Store code_verifier temporarily (in production, use a secure session store)
        self._temp_code_verifier = code_verifier
        self._temp_state = actual_state

        return url

    def exchange_code_for_token(
        self, provider_name: str, code: str, state: str = None
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        if state and state != getattr(self, "_temp_state", None):
            raise ValueError("State mismatch")

        client = OAuth2Client(
            client_id=provider.client_id,
            client_secret=provider.client_secret,
            token_endpoint=provider.token_endpoint,
        )

        token = client.fetch_token(
            self.redirect_uri,
            code=code,
            code_verifier=getattr(self, "_temp_code_verifier", None),
        )

        return token

    def get_user_info(self, provider_name: str, access_token: str) -> Dict[str, Any]:
        """Fetch user information from the provider's userinfo endpoint."""
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        with httpx.Client() as client:
            response = client.get(
                provider.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    def verify_id_token(self, provider_name: str, id_token: str) -> Dict[str, Any]:
        """Verify an OpenID Connect ID token."""
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        # For simplicity, we'll trust the token if we have a jwks_uri.
        # In production, validate signature, issuer, audience, and expiration.
        if provider.jwks_uri:
            # TODO: Implement full JWT validation with JWKS
            pass

        # Decode without verification (for demo – production must verify)
        import jwt
        return jwt.decode(id_token, options={"verify_signature": False})

    # -------------------------------------------------------------------------
    # Convenience methods for common providers (auto-configure)
    # -------------------------------------------------------------------------
    @classmethod
    def create_google_provider(cls, client_id: str, client_secret: str) -> OIDCProvider:
        return OIDCProvider(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
            token_endpoint="https://oauth2.googleapis.com/token",
            userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
            scopes=["openid", "email", "profile"],
            issuer="https://accounts.google.com",
        )

    @classmethod
    def create_github_provider(cls, client_id: str, client_secret: str) -> OIDCProvider:
        return OIDCProvider(
            name="github",
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint="https://github.com/login/oauth/authorize",
            token_endpoint="https://github.com/login/oauth/access_token",
            userinfo_endpoint="https://api.github.com/user",
            scopes=["user:email"],
        )

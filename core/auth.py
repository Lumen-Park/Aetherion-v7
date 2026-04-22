"""
Authentication & Authorization Manager
Supports API Key and JWT token validation.
"""

import os
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


class AuthManager:
    """Handles authentication and authorization for Aetherion operations."""

    def __init__(self):
        self.auth_enabled = os.getenv("AETHERION_REQUIRE_AUTH", "false").lower() == "true"
        self.api_keys = self._load_api_keys()
        self.jwt_secret = os.getenv("AETHERION_JWT_SECRET", "")

    def _load_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from environment or config file."""
        keys = {}
        # Format: AETHERION_API_KEYS="key1:admin,key2:operator"
        key_string = os.getenv("AETHERION_API_KEYS", "")
        if key_string:
            for item in key_string.split(","):
                if ":" in item:
                    key, role = item.split(":", 1)
                    keys[self._hash_key(key.strip())] = {
                        "role": role.strip(),
                        "created": datetime.now().isoformat()
                    }
        return keys

    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify an API key and return its associated metadata."""
        if not api_key:
            return None
        hashed = self._hash_key(api_key)
        return self.api_keys.get(hashed)

    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return its payload."""
        if not JWT_AVAILABLE or not self.jwt_secret:
            return None
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except Exception:
            return None

    def authenticate(self, auth_token: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Main authentication entry point.
        Returns user/role info if authenticated, None otherwise.
        """
        if not self.auth_enabled:
            return {"role": "admin", "auth_disabled": True}

        if not auth_token:
            return None

        # Try API key first
        api_key_info = self.verify_api_key(auth_token)
        if api_key_info:
            return api_key_info

        # Then try JWT
        jwt_payload = self.verify_jwt(auth_token)
        if jwt_payload:
            return jwt_payload

        return None

    def authorize(self, auth_info: Dict[str, Any], required_role: str = "operator") -> bool:
        """
        Check if authenticated identity has the required role.
        Roles: admin > operator > viewer
        """
        if not self.auth_enabled:
            return True

        role = auth_info.get("role", "viewer")
        role_hierarchy = {"admin": 3, "operator": 2, "viewer": 1}
        required_level = role_hierarchy.get(required_role, 1)
        user_level = role_hierarchy.get(role, 0)
        return user_level >= required_level

    @classmethod
    def generate_api_key(cls) -> str:
        """Generate a new secure API key."""
        return secrets.token_urlsafe(32)

    @classmethod
    def generate_jwt(cls, user_id: str, role: str, secret: str, expires_in_hours: int = 24) -> str:
        """Generate a JWT token for a user."""
        if not JWT_AVAILABLE:
            raise ImportError("PyJWT not installed. Run: pip install PyJWT")
        payload = {
            "sub": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, secret, algorithm="HS256")

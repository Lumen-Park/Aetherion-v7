#!/usr/bin/env python3
"""Generate a new API key for Aetherion."""

from core.auth import AuthManager

key = AuthManager.generate_api_key()
print(f"Generated API Key: {key}")
print("\nAdd to .env as part of AETHERION_API_KEYS:")
print(f"AETHERION_API_KEYS={key}:admin")

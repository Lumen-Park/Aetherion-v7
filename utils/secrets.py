"""
Secrets Manager – Encrypt/decrypt sensitive configuration values.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class SecretsManager:
    _fernet = None

    @classmethod
    def _get_fernet(cls) -> Fernet:
        if cls._fernet is not None:
            return cls._fernet
        # Derive key from a master password (set in environment, never committed)
        master_password = os.getenv("AETHERION_MASTER_KEY")
        if not master_password:
            raise RuntimeError("AETHERION_MASTER_KEY environment variable not set")
        salt = b'aetherion_salt_2026'  # In production, store salt securely
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        cls._fernet = Fernet(key)
        return cls._fernet

    @classmethod
    def decrypt(cls, encrypted_value: str) -> str:
        if not encrypted_value.startswith("ENC["):
            return encrypted_value  # Not encrypted
        b64_data = encrypted_value[4:-1]  # Strip ENC[ and ]
        return cls._get_fernet().decrypt(b64_data.encode()).decode()

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Utility to encrypt values for storage (run once offline)."""
        encrypted = cls._get_fernet().encrypt(plaintext.encode())
        return f"ENC[{base64.urlsafe_b64encode(encrypted).decode()}]"

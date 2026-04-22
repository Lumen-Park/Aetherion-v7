"""
Secrets Manager – Encrypt/decrypt sensitive configuration values.
Uses Fernet symmetric encryption with a key derived from a master password.
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
        """Lazily initialize the Fernet instance using the master key."""
        if cls._fernet is not None:
            return cls._fernet

        master_password = os.getenv("AETHERION_MASTER_KEY")
        if not master_password:
            raise RuntimeError(
                "AETHERION_MASTER_KEY environment variable not set. "
                "This key is required to decrypt secrets."
            )

        # Use a fixed salt (in production, consider storing salt securely)
        salt = b'aetherion_salt_2026'
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
        """
        Decrypt a value if it is encrypted (format: ENC[base64]).
        If the value is not encrypted, return it unchanged.
        """
        if not encrypted_value or not encrypted_value.startswith("ENC["):
            return encrypted_value

        # Strip ENC[ and ]
        b64_data = encrypted_value[4:-1]
        try:
            decoded = base64.urlsafe_b64decode(b64_data.encode())
            return cls._get_fernet().decrypt(decoded).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt secret: {e}")

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """
        Encrypt a plaintext value and return it in ENC[...] format.
        Use this utility offline to generate encrypted strings for .env.
        """
        if not plaintext:
            return ""
        encrypted = cls._get_fernet().encrypt(plaintext.encode())
        b64_encrypted = base64.urlsafe_b64encode(encrypted).decode()
        return f"ENC[{b64_encrypted}]"

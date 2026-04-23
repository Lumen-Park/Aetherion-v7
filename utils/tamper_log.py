"""
Tamper‑Proof Audit Log – Append‑only, cryptographically chained log.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class TamperProofLogger:
    """Append‑only, cryptographically chained audit log."""

    def __init__(self, log_path: str, private_key_path: Optional[str] = None):
        self.log_path = log_path
        self.private_key = None
        if private_key_path and os.path.exists(private_key_path):
            with open(private_key_path, "rb") as f:
                self.private_key = load_pem_private_key(
                    f.read(), password=None
                )

    def _compute_hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def _sign_entry(self, entry_hash: str) -> Optional[str]:
        if not self.private_key:
            return None
        signature = self.private_key.sign(
            entry_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return signature.hex()

    def write(self, event_type: str, data: Dict[str, Any]) -> str:
        """Append a tamper‑proof entry to the log."""
        # Read the last entry's hash
        prev_hash = self._get_last_hash()

        # Create new entry
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data,
            "prev_hash": prev_hash,
        }
        entry_json = json.dumps(entry, sort_keys=True)
        entry["hash"] = self._compute_hash(entry_json)
        entry["signature"] = self._sign_entry(entry["hash"])

        # Append to log file
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry["hash"]

    def _get_last_hash(self) -> Optional[str]:
        """Retrieve the hash of the most recent log entry."""
        if not os.path.exists(self.log_path):
            return None
        with open(self.log_path, "rb") as f:
            try:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode().strip()
            if last_line:
                return json.loads(last_line).get("hash")
        return None

    def verify(self, public_key_path: str) -> bool:
        """Verify the integrity of the entire log."""
        # Load public key
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        prev_hash = None
        with open(self.log_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                # Verify chain
                if entry.get("prev_hash") != prev_hash:
                    return False
                # Recompute hash
                entry_copy = entry.copy()
                del entry_copy["hash"]
                del entry_copy["signature"]
                computed_hash = self._compute_hash(
                    json.dumps(entry_copy, sort_keys=True)
                )
                if computed_hash != entry["hash"]:
                    return False
                # Verify signature
                if entry.get("signature") and public_key:
                    try:
                        public_key.verify(
                            bytes.fromhex(entry["signature"]),
                            entry["hash"].encode(),
                            padding.PSS(
                                mgf=padding.MGF1(hashes.SHA256()),
                                salt_length=padding.PSS.MAX_LENGTH,
                            ),
                            hashes.SHA256(),
                        )
                    except Exception:
                        return False
                prev_hash = entry["hash"]
        return True

"""
Aetherion Logger – JSON structured logs for observability.
Includes log rotation to prevent unbounded disk usage.
"""

import json
import os
import time


class AetherionLogger:
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_LOG_FILES = 10

    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self._rotate_if_needed()
        self.log_file = os.path.join(log_dir, "aetherion.jsonl")
        open(self.log_file, "a").close()

    def _rotate_if_needed(self):
        current = os.path.join(self.log_dir, "aetherion.jsonl")
        if not os.path.exists(current):
            return
        size = os.path.getsize(current)
        if size < self.MAX_LOG_SIZE:
            return
        for i in range(self.MAX_LOG_FILES, 1, -1):
            src = f"{current}.{i-1}"
            dst = f"{current}.{i}"
            if os.path.exists(src):
                os.rename(src, dst)
            if i >= self.MAX_LOG_FILES and os.path.exists(dst):
                os.remove(dst)
        if os.path.exists(current):
            os.rename(current, f"{current}.1")
        self._cleanup_rotated()

    def _cleanup_rotated(self):
        current = os.path.join(self.log_dir, "aetherion.jsonl")
        for i in range(self.MAX_LOG_FILES + 1, 100):
            path = f"{current}.{i}"
            if os.path.exists(path):
                os.remove(path)
            else:
                break

    def log(self, level: str, message: str, **kwargs):
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs,
        }
        self._rotate_if_needed()
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def info(self, msg: str, **kwargs):
        self.log("INFO", msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self.log("ERROR", msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        self.log("DEBUG", msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self.log("WARNING", msg, **kwargs)

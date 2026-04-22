"""
Aetherion Logger – JSON structured logs.
"""

import json
import os
import time


class AetherionLogger:
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(
            log_dir, f"aetherion_{int(time.time())}.jsonl"
        )

    def log(self, level: str, message: str, **kwargs):
        entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs,
        }
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

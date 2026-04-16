"""
Sandbox – Execute generated code in isolated Docker container.
"""

import subprocess
import tempfile
import os
from typing import Dict

class SandboxExecutor:
    def __init__(self, image: str = "python:3.11-slim", timeout: int = 30):
        self.image = image
        self.timeout = timeout
    
    def run(self, code: str) -> Dict:
        """Execute Python code in a disposable container."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "256m",
                "--cpus", "0.5",
                "-v", f"{temp_path}:/app/script.py:ro",
                self.image,
                "python", "/app/script.py"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "passed": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Execution timed out", "returncode": -1, "passed": False}
        finally:
            os.unlink(temp_path)

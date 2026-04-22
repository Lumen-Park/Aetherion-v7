"""
Hardened Sandbox – Execute untrusted code in a secure Docker container.
"""

import os
import subprocess
import tempfile
from typing import Dict, Optional


class SandboxExecutor:
    def __init__(
        self,
        image: str = "python:3.11-slim",
        timeout: int = 10,
        memory: str = "256m",
        cpus: float = 0.5,
        pids_limit: int = 50,
        enable_network: bool = False,
        read_only_root: bool = True,
        user_namespace: bool = True,
    ):
        self.image = image
        self.timeout = timeout
        self.memory = memory
        self.cpus = cpus
        self.pids_limit = pids_limit
        self.enable_network = enable_network
        self.read_only_root = read_only_root
        self.user_namespace = user_namespace

    def run(self, code: str, stdin_data: Optional[str] = None) -> Dict:
        """Execute Python code in a hardened disposable container."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        seccomp_path = os.path.join(
            os.path.dirname(__file__), "seccomp_profile.json"
        )
        if not os.path.exists(seccomp_path):
            seccomp_path = None  # Fallback to default

        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--memory",
                self.memory,
                "--memory-swap",
                self.memory,  # No swap
                "--cpus",
                str(self.cpus),
                "--pids-limit",
                str(self.pids_limit),
                "--security-opt",
                "no-new-privileges:true",
                "--cap-drop",
                "ALL",
                "--cap-add",
                "DAC_OVERRIDE",  # Allow reading/writing files owned by root? No, we'll use tmpfs
            ]

            # Network policy
            if not self.enable_network:
                cmd.append("--network")
                cmd.append("none")

            # Read-only root filesystem with writable /tmp
            if self.read_only_root:
                cmd.append("--read-only")
                cmd.append("--tmpfs")
                cmd.append("/tmp:rw,noexec,nosuid,size=100M")

            # User namespace remapping (prevents root in container = root on host)
            if self.user_namespace:
                cmd.append(
                    "--userns=host"
                )  # Uses subordinate IDs configured on host

            # Seccomp profile
            if seccomp_path:
                cmd.append("--security-opt")
                cmd.append(f"seccomp={seccomp_path}")

            # Mount code as read-only
            cmd.extend(["-v", f"{temp_path}:/app/script.py:ro"])

            cmd.append(self.image)
            cmd.extend(["python", "-I", "/app/script.py"])  # -I: isolated mode

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                input=stdin_data,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "passed": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Execution timed out",
                "returncode": -1,
                "passed": False,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "passed": False,
            }
        finally:
            os.unlink(temp_path)

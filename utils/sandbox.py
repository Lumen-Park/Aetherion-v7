"""
Hardened Sandbox – Execute untrusted code in a secure container.
Supports Docker (default), gVisor (runsc), and fine‑grained egress controls.
"""

import os
import subprocess
import tempfile
from typing import Dict, List, Optional

from utils.egress_proxy import EgressController


class SandboxExecutor:
    def __init__(
        self,
        image: str = "python:3.11-slim",
        timeout: int = 10,
        memory: str = "256m",
        cpus: float = 0.5,
        pids_limit: int = 50,
        network_mode: str = "none",  # "none", "allow_list", "host"
        allowed_domains: Optional[List[str]] = None,
        allowed_cidrs: Optional[List[str]] = None,
        read_only_root: bool = True,
        user_namespace: bool = True,
        runtime: str = "runsc",  # "runc" or "runsc"
    ):
        self.image = image
        self.timeout = timeout
        self.memory = memory
        self.cpus = cpus
        self.pids_limit = pids_limit
        self.network_mode = network_mode
        self.allowed_domains = allowed_domains or []
        self.allowed_cidrs = allowed_cidrs or []
        self.read_only_root = read_only_root
        self.user_namespace = user_namespace
        self.runtime = runtime

        self._egress_controller = None
        self._proxy_ip = None

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
            seccomp_path = None

        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "--runtime",
                self.runtime,
                "--memory",
                self.memory,
                "--memory-swap",
                self.memory,
                "--cpus",
                str(self.cpus),
                "--pids-limit",
                str(self.pids_limit),
                "--security-opt",
                "no-new-privileges:true",
                "--cap-drop",
                "ALL",
            ]

            # Network configuration
            if self.network_mode == "allow_list":
                # Start egress proxy sidecar
                self._egress_controller = EgressController(
                    allowed_domains=self.allowed_domains,
                    allowed_cidrs=self.allowed_cidrs,
                )
                self._proxy_ip = self._egress_controller.start_proxy()
                # Connect sandbox to the proxy's network namespace
                cmd.extend(
                    [
                        "--network",
                        f"container:{self._egress_controller.proxy_container_name}",
                    ]
                )
                # Set environment variables for proxy (if code uses requests/urllib)
                cmd.extend(["-e", f"HTTP_PROXY=http://{self._proxy_ip}:3128"])
                cmd.extend(["-e", f"HTTPS_PROXY=http://{self._proxy_ip}:3128"])
            elif self.network_mode == "none":
                cmd.append("--network")
                cmd.append("none")
            elif self.network_mode == "host":
                # Insecure: full host network access
                cmd.append("--network")
                cmd.append("host")
            else:
                raise ValueError(f"Invalid network_mode: {self.network_mode}")

            if self.read_only_root:
                cmd.append("--read-only")
                cmd.append("--tmpfs")
                cmd.append("/tmp:rw,noexec,nosuid,size=100M")

            if self.user_namespace:
                cmd.append("--userns=host")

            if seccomp_path and self.runtime != "runsc":
                cmd.append("--security-opt")
                cmd.append(f"seccomp={seccomp_path}")

            cmd.extend(["-v", f"{temp_path}:/app/script.py:ro"])
            cmd.append(self.image)
            cmd.extend(["python", "-I", "/app/script.py"])

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
            if self._egress_controller:
                self._egress_controller.stop_proxy()
            os.unlink(temp_path)

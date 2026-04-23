"""
Egress Proxy – Sidecar forward proxy with domain/IP allow‑list enforcement.
Runs in a Docker container and exposes a SOCKS5 proxy for the sandbox.
"""

import os
import subprocess
import tempfile
import time
from typing import List, Optional
import json


class EgressController:
    """
    Manages an egress proxy sidecar that enforces network allow‑lists.
    """

    def __init__(self, allowed_domains: Optional[List[str]] = None,
                 allowed_cidrs: Optional[List[str]] = None):
        self.allowed_domains = allowed_domains or []
        self.allowed_cidrs = allowed_cidrs or []
        self.proxy_container_name = None
        self.proxy_port = 1080  # Default SOCKS5 port

    def _generate_squid_config(self) -> str:
        """
        Generate a Squid configuration with the specified allow‑lists.
        """
        config_lines = [
            "http_port 3128",
            "acl allowed_domains dstdomain .localhost",
            "acl allowed_ips dst 127.0.0.1",
        ]

        # Add domain allow‑list
        for domain in self.allowed_domains:
            config_lines.append(f"acl allowed_domains dstdomain {domain}")
            config_lines.append(f"acl allowed_domains dstdomain .{domain}")  # subdomains

        # Add CIDR allow‑list
        for cidr in self.allowed_cidrs:
            config_lines.append(f"acl allowed_ips dst {cidr}")

        # Default deny and allow rules
        config_lines.extend([
            "http_access deny !allowed_domains",
            "http_access deny !allowed_ips",
            "http_access allow allowed_domains",
            "http_access allow allowed_ips",
            "http_access deny all",
        ])

        return "\n".join(config_lines)

    def start_proxy(self) -> str:
        """
        Start a Squid proxy container with the configured allow‑lists.
        Returns the container name.
        """
        config_content = self._generate_squid_config()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write(config_content)
            config_path = f.name

        self.proxy_container_name = f"aetherion-egress-{int(time.time())}"

        cmd = [
            "docker", "run", "-d", "--rm",
            "--name", self.proxy_container_name,
            "-v", f"{config_path}:/etc/squid/squid.conf:ro",
            "--network", "bridge",  # Isolated bridge network
            "sameersbn/squid:3.5.27-2"
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        # Give Squid a moment to start
        time.sleep(2)

        # Get the container's IP address on the bridge network
        inspect_cmd = ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", self.proxy_container_name]
        result = subprocess.run(inspect_cmd, capture_output=True, text=True, check=True)
        proxy_ip = result.stdout.strip()

        # Clean up temp file
        os.unlink(config_path)

        return proxy_ip

    def stop_proxy(self):
        """Stop and remove the proxy container."""
        if self.proxy_container_name:
            subprocess.run(["docker", "stop", self.proxy_container_name], capture_output=True)
            self.proxy_container_name = None

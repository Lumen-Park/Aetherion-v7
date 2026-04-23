import time
from typing import Any, Dict, Optional

import httpx

from agents.colleges.all_colleges import AGENT_REGISTRY


class AgentClient:
    """
    HTTP client for calling microservice agents.
    Assumes each agent runs at http://<agent_name_lower>:8000 .
    """

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._cache: Dict[str, bool] = {}

    def _get_service_url(self, agent_name: str) -> str:
        # Convert CamelCase to kebab-case (or just lowercase) for Docker service name
        service_name = agent_name.lower()
        return f"http://{service_name}:8000"

    async def analyze(
        self, agent_name: str, goal: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Call an agent's /analyze endpoint."""
        url = f"{self._get_service_url(agent_name)}/analyze"
        payload = {"goal": goal, "context": context or {}}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                start = time.time()
                response = await client.post(url, json=payload)
                response.raise_for_status()
                from api.metrics import agent_latency_seconds

                agent_latency_seconds.labels(agent_name=agent_name).observe(
                    time.time() - start
                )
                return response.json()
            except Exception as e:
                raise RuntimeError(f"Agent {agent_name} call failed: {e}")

    async def health_check(self, agent_name: str) -> bool:
        """Quick health check."""
        url = f"{self._get_service_url(agent_name)}/health"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                return response.status_code == 200
            except Exception:
                return False

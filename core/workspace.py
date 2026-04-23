"""
Workspace Manager – Multi‑tenant isolation for team deployments.
"""

import os
import json
from typing import Dict, Optional
from core.memory import KnowledgeGraph
from agents.governance.meta_orchestrator import MetaOrchestrator


DEFAULT_CONSTITUTION = {
    "judges": {
        "Critic": {
            "prompt": "Find the strongest argument against this output. Be skeptical.",
            "enabled": True,
            "weight": 1.0
        },
        "Security": {
            "prompt": "Identify any security vulnerabilities, unsafe patterns, or exposed secrets. Be strict. REJECT if any found.",
            "enabled": True,
            "weight": 1.0
        },
        "Alignment": {
            "prompt": "Does this output exactly match the user's original request? Flag any deviation.",
            "enabled": True,
            "weight": 1.0
        },
        "Constraint": {
            "prompt": "Is this within reasonable scope and resource limits? Flag over-engineering.",
            "enabled": True,
            "weight": 1.0
        },
        "Evaluator": {
            "prompt": "Score overall quality 0-10. Consider correctness, efficiency, readability.",
            "enabled": True,
            "weight": 1.0
        },
        "Documentation": {
            "prompt": "Can a stranger understand and use this output? Is it well-documented?",
            "enabled": True,
            "weight": 1.0
        },
        "AetherionPrime": {
            "prompt": "Given all perspectives, what is the safest and most reasonable path forward?",
            "enabled": True,
            "weight": 1.0
        }
    },
    "thresholds": {
        "approved": 7.0,
        "revision": 5.0
    }
}


class WorkspaceManager:
    """Manages isolated workspaces with shared Ollama backend."""

    def __init__(self, base_dir: str = "./workspaces", shared_ollama_host: str = "http://localhost:11434"):
        self.base_dir = base_dir
        self.shared_ollama_host = shared_ollama_host
        self.workspaces: Dict[str, Dict] = {}
        os.makedirs(base_dir, exist_ok=True)

    def _get_workspace_path(self, workspace_id: str) -> str:
        return os.path.join(self.base_dir, workspace_id)

    def _get_constitution_path(self, workspace_id: str) -> str:
        return os.path.join(self._get_workspace_path(workspace_id), "constitution.json")

    def get_constitution(self, workspace_id: str) -> dict:
        """Return the custom constitution for the workspace, or the default."""
        path = self._get_constitution_path(workspace_id)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return DEFAULT_CONSTITUTION.copy()

    def update_constitution(self, workspace_id: str, constitution: dict) -> bool:
        """Save a custom constitution for the workspace."""
        workspace_path = self._get_workspace_path(workspace_id)
        if not os.path.exists(workspace_path):
            return False
        path = self._get_constitution_path(workspace_id)
        with open(path, 'w') as f:
            json.dump(constitution, f, indent=2)
        # Refresh in‑memory cache
        if workspace_id in self.workspaces:
            self.workspaces[workspace_id]["constitution"] = constitution
        return True

    def get_knowledge_graph(self, workspace_id: str) -> KnowledgeGraph:
        persist_dir = os.path.join(self.base_dir, workspace_id, "memory")
        return KnowledgeGraph(persist_dir=persist_dir)

    def get_orchestrator(self, workspace_id: str) -> MetaOrchestrator:
        workspace_path = self._get_workspace_path(workspace_id)
        if not os.path.exists(workspace_path):
            raise ValueError(f"Workspace '{workspace_id}' does not exist.")

        if workspace_id not in self.workspaces:
            self.workspaces[workspace_id] = {
                "kg": self.get_knowledge_graph(workspace_id),
                "constitution": self.get_constitution(workspace_id),
            }

        kg = self.workspaces[workspace_id]["kg"]
        orchestrator = MetaOrchestrator()
        orchestrator.knowledge_graph = kg
        orchestrator.llm.host = self.shared_ollama_host
        # Inject constitution into orchestrator for Council
        orchestrator.workspace_constitution = self.workspaces[workspace_id]["constitution"]
        return orchestrator

    def create_workspace(self, workspace_id: str) -> bool:
        workspace_path = self._get_workspace_path(workspace_id)
        if os.path.exists(workspace_path):
            return False
        os.makedirs(workspace_path, exist_ok=True)
        return True

    def delete_workspace(self, workspace_id: str) -> bool:
        import shutil
        workspace_path = self._get_workspace_path(workspace_id)
        if not os.path.exists(workspace_path):
            return False
        shutil.rmtree(workspace_path)
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
        return True

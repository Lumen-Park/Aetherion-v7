"""
Workspace Manager – Multi‑tenant isolation for team deployments.
"""

import os
from typing import Dict, Optional

from agents.governance.meta_orchestrator import MetaOrchestrator
from core.memory import KnowledgeGraph


class WorkspaceManager:
    """Manages isolated workspaces with shared Ollama backend."""

    def __init__(
        self,
        base_dir: str = "./workspaces",
        shared_ollama_host: str = "http://localhost:11434",
    ):
        self.base_dir = base_dir
        self.shared_ollama_host = shared_ollama_host
        self.workspaces: Dict[str, Dict] = {}
        os.makedirs(base_dir, exist_ok=True)

    def get_knowledge_graph(self, workspace_id: str) -> KnowledgeGraph:
        """Return an isolated knowledge graph for the workspace."""
        persist_dir = os.path.join(self.base_dir, workspace_id, "memory")
        return KnowledgeGraph(persist_dir=persist_dir)

    def get_orchestrator(self, workspace_id: str) -> MetaOrchestrator:
        """
        Return a MetaOrchestrator configured for the workspace.
        Uses shared Ollama but isolated knowledge graph and council config.
        """
        workspace_path = os.path.join(self.base_dir, workspace_id)
        if not os.path.exists(workspace_path):
            raise ValueError(f"Workspace '{workspace_id}' does not exist.")

        if workspace_id not in self.workspaces:
            self.workspaces[workspace_id] = {
                "kg": self.get_knowledge_graph(workspace_id),
                "config": {},
            }

        kg = self.workspaces[workspace_id]["kg"]
        orchestrator = MetaOrchestrator()
        orchestrator.knowledge_graph = kg
        orchestrator.llm.host = self.shared_ollama_host
        return orchestrator

    def create_workspace(self, workspace_id: str) -> bool:
        """Provision a new workspace."""
        workspace_path = os.path.join(self.base_dir, workspace_id)
        if os.path.exists(workspace_path):
            return False
        os.makedirs(workspace_path, exist_ok=True)
        return True

    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace and all its data."""
        import shutil

        workspace_path = os.path.join(self.base_dir, workspace_id)
        if not os.path.exists(workspace_path):
            return False
        shutil.rmtree(workspace_path)
        if workspace_id in self.workspaces:
            del self.workspaces[workspace_id]
        return True

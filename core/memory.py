"""
Aetherion Memory System – ChromaDB knowledge graph + agent reputation.
"""

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

import chromadb


@dataclass
class MemoryEntry:
    key: str
    value: Any
    confidence: float
    source: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


class KnowledgeGraph:
    """Vector-backed persistent memory with source tracking."""

    def __init__(self, persist_dir: str = "./memory"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            "aetherion_memory"
        )
        self.reputation = AgentReputation(persist_dir)
        self.archivist = Archivist(persist_dir)

    def store(
        self, key: str, value: Any, confidence: float, source: str = "unknown"
    ):
        if confidence < 0.45:
            return False
        doc_id = f"{key}_{int(time.time())}"
        metadata = {
            "confidence": confidence,
            "source": source,
            "timestamp": time.time(),
        }
        self.collection.add(
            documents=[json.dumps(value)], metadatas=[metadata], ids=[doc_id]
        )
        self.archivist.log_store(key, confidence, source)
        return True

    def query(self, query: str, n_results: int = 5) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query], n_results=n_results
        )
        formatted = []
        for i, doc in enumerate(results["documents"][0]):
            formatted.append(
                {
                    "content": json.loads(doc),
                    "metadata": results["metadatas"][0][i],
                    "id": results["ids"][0][i],
                }
            )
        return formatted

    def get_relevant_context(self, query: str) -> str:
        results = self.query(query, n_results=3)
        context_parts = []
        for r in results:
            if r["metadata"]["confidence"] >= 0.5:
                context_parts.append(json.dumps(r["content"]))
        return "\n".join(context_parts)


class AgentReputation:
    def __init__(self, persist_dir: str):
        self.reputation_file = os.path.join(persist_dir, "reputation.json")
        self.reputation = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.reputation_file):
            with open(self.reputation_file, "r") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.reputation_file, "w") as f:
            json.dump(self.reputation, f, indent=2)

    def update(self, agent_name: str, was_correct: bool):
        current = self.reputation.get(agent_name, {"correct": 0, "total": 0})
        current["total"] += 1
        if was_correct:
            current["correct"] += 1
        self.reputation[agent_name] = current
        self._save()

    def get_weight(self, agent_name: str) -> float:
        if agent_name not in self.reputation:
            return 1.0
        data = self.reputation[agent_name]
        if data["total"] < 5:
            return 1.0
        accuracy = data["correct"] / data["total"]
        return min(1.5, max(0.7, accuracy))


class Archivist:
    def __init__(self, persist_dir: str):
        self.archive_dir = os.path.join(persist_dir, "archive")
        os.makedirs(self.archive_dir, exist_ok=True)

    def log_store(self, key: str, confidence: float, source: str):
        pass

    def log_rejection(self, task_id: str, reason: str, pattern: str):
        entry = {
            "task_id": task_id,
            "reason": reason,
            "pattern": pattern,
            "timestamp": time.time(),
        }
        filepath = os.path.join(self.archive_dir, f"reject_{task_id}.json")
        with open(filepath, "w") as f:
            json.dump(entry, f, indent=2)

    def get_rejection_patterns(self, limit: int = 10) -> List[Dict]:
        patterns = []
        files = sorted(os.listdir(self.archive_dir), reverse=True)[:limit]
        for fname in files:
            if fname.startswith("reject_"):
                with open(os.path.join(self.archive_dir, fname), "r") as f:
                    patterns.append(json.load(f))
        return patterns

"""
Task State Manager – ensures tasks follow a valid, non‑reversible graph.
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional, Set


class TaskState(Enum):
    QUEUED = auto()
    REFINING = auto()
    CURATING = auto()
    RESEARCHING = auto()
    DEVELOPING = auto()
    REVIEWING = auto()
    TESTING = auto()
    SANITIZING = auto()
    FORENSICS = auto()
    EDGE_CASES = auto()
    EVALUATING = auto()
    COUNCIL = auto()
    HUMAN_REVIEW = auto()
    APPROVED = auto()
    REJECTED = auto()
    REVISION = auto()
    FAILED = auto()
    DONE = auto()


VALID_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.QUEUED: {TaskState.REFINING},
    TaskState.REFINING: {TaskState.CURATING},
    TaskState.CURATING: {TaskState.RESEARCHING},
    TaskState.RESEARCHING: {TaskState.DEVELOPING},
    TaskState.DEVELOPING: {TaskState.REVIEWING},
    TaskState.REVIEWING: {TaskState.TESTING, TaskState.DEVELOPING},
    TaskState.TESTING: {TaskState.SANITIZING, TaskState.DEVELOPING},
    TaskState.SANITIZING: {TaskState.FORENSICS},
    TaskState.FORENSICS: {TaskState.EDGE_CASES},
    TaskState.EDGE_CASES: {TaskState.EVALUATING},
    TaskState.EVALUATING: {TaskState.COUNCIL},
    TaskState.COUNCIL: {TaskState.HUMAN_REVIEW},
    TaskState.HUMAN_REVIEW: {
        TaskState.APPROVED,
        TaskState.REJECTED,
        TaskState.REVISION,
        TaskState.FAILED,
    },
    TaskState.REVISION: {TaskState.DEVELOPING, TaskState.FAILED},
    TaskState.APPROVED: {TaskState.DONE},
    TaskState.REJECTED: {TaskState.DONE},
    TaskState.FAILED: set(),
    TaskState.DONE: set(),
}


@dataclass
class TaskContext:
    task_id: str
    state: TaskState
    goal: str
    refined_goal: Optional[str] = None
    expert_panel: list = field(default_factory=list)
    research_findings: Optional[str] = None
    code_output: Optional[str] = None
    test_results: Optional[Dict] = None
    council_verdict: Optional[Dict] = None
    confidence: float = 0.0
    retry_count: int = 0
    state_history: list = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    error: Optional[str] = None
    error_type: Optional[str] = None
    override: bool = False
    override_operator: Optional[str] = None
    override_reason: Optional[str] = None
    override_timestamp: Optional[float] = None
    sanitized_output: Optional[str] = None
    forensic_report: Optional[Dict] = None
    edge_cases: Optional[list] = None


class TaskStateManager:
    STATE_OUTPUT_REQUIREMENTS = {
        TaskState.REFINING: ["refined_goal"],
        TaskState.CURATING: ["expert_panel"],
        TaskState.RESEARCHING: ["research_findings"],
        TaskState.DEVELOPING: ["code_output"],
        TaskState.TESTING: ["test_results"],
        TaskState.COUNCIL: ["council_verdict"],
    }

    def __init__(self, confidence_threshold: float = 0.45):
        self.threshold = confidence_threshold
        self.current_context: Optional[TaskContext] = None
        self.state_counter: Dict[TaskState, int] = {}
        self.logger = None

    def _get_logger(self):
        if self.logger is None:
            from utils.logger import AetherionLogger

            self.logger = AetherionLogger()
        return self.logger

    def start_task(self, task_id: str, goal: str) -> TaskContext:
        self.current_context = TaskContext(
            task_id=task_id, state=TaskState.QUEUED, goal=goal
        )
        return self.current_context

    def transition(
        self, new_state: TaskState, context_update: Dict[str, Any]
    ) -> TaskContext:
        if not self.current_context:
            raise RuntimeError("No active task")

        if self.detect_loop(new_state):
            self._get_logger().warning(
                f"Loop detected for state {new_state.name}. Forcing FAILED."
            )
            new_state = TaskState.FAILED
            context_update["error"] = (
                f"Forced FAILED due to loop detection on {new_state.name}"
            )
            context_update["loop_detected"] = True

        current = self.current_context.state
        if new_state not in VALID_TRANSITIONS[current]:
            raise ValueError(
                f"Invalid transition: {current.name} -> {new_state.name}"
            )

        required = self.STATE_OUTPUT_REQUIREMENTS.get(new_state, [])
        for req_field in required:
            if req_field not in context_update and not getattr(
                self.current_context, req_field, None
            ):
                raise ValueError(
                    f"State {new_state.name} requires field '{req_field}'"
                )

        update_dict = {
            "state": new_state,
            "updated_at": time.time(),
            "state_history": self.current_context.state_history
            + [current.name],
        }
        update_dict.update(context_update)

        self.current_context = TaskContext(
            **{**self.current_context.__dict__, **update_dict}
        )
        self.state_counter[new_state] = (
            self.state_counter.get(new_state, 0) + 1
        )

        return self.current_context

    def should_store_to_memory(self) -> bool:
        if not self.current_context:
            return False
        return self.current_context.confidence >= self.threshold

    def detect_loop(self, state: TaskState) -> bool:
        return self.state_counter.get(state, 0) >= 3

    def to_json(self) -> str:
        return json.dumps(self.current_context.__dict__, indent=2, default=str)

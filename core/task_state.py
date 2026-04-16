"""
Task State Manager – ensures tasks follow a valid, non‑reversible graph.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import time
import json

class TaskState(Enum):
    QUEUED = auto()
    REFINING = auto()       # Goal Refiner
    CURATING = auto()       # Curator selects panel
    RESEARCHING = auto()    # Researcher + colleges
    DEVELOPING = auto()     # Developer writes code
    REVIEWING = auto()      # Partner reviews
    TESTING = auto()        # Tester executes
    SANITIZING = auto()     # Sanitizer cleans output
    FORENSICS = auto()      # Forensic fact‑check
    EDGE_CASES = auto()     # Edge‑case generation
    EVALUATING = auto()     # Council deliberation prep
    COUNCIL = auto()        # 7‑judge vote
    HUMAN_REVIEW = auto()   # Awaiting human decision
    APPROVED = auto()
    REJECTED = auto()
    REVISION = auto()       # Send back to DEVELOPING
    DONE = auto()

# Valid transitions (directed edges)
VALID_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.QUEUED: {TaskState.REFINING},
    TaskState.REFINING: {TaskState.CURATING},
    TaskState.CURATING: {TaskState.RESEARCHING},
    TaskState.RESEARCHING: {TaskState.DEVELOPING},
    TaskState.DEVELOPING: {TaskState.REVIEWING},
    TaskState.REVIEWING: {TaskState.TESTING, TaskState.DEVELOPING},  # retry allowed
    TaskState.TESTING: {TaskState.SANITIZING, TaskState.DEVELOPING}, # retry
    TaskState.SANITIZING: {TaskState.FORENSICS},
    TaskState.FORENSICS: {TaskState.EDGE_CASES},
    TaskState.EDGE_CASES: {TaskState.EVALUATING},
    TaskState.EVALUATING: {TaskState.COUNCIL},
    TaskState.COUNCIL: {TaskState.HUMAN_REVIEW},
    TaskState.HUMAN_REVIEW: {TaskState.APPROVED, TaskState.REJECTED, TaskState.REVISION},
    TaskState.REVISION: {TaskState.DEVELOPING},
    TaskState.APPROVED: {TaskState.DONE},
    TaskState.REJECTED: {TaskState.DONE},
    TaskState.DONE: set(),
}

@dataclass
class TaskContext:
    """Immutable snapshot of task progress."""
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

class TaskStateManager:
    """Enforces valid state transitions and confidence‑gated storage."""
    
    def __init__(self, confidence_threshold: float = 0.45):
        self.threshold = confidence_threshold
        self.current_context: Optional[TaskContext] = None
        self.state_counter: Dict[TaskState, int] = {}  # for loop detection
    
    def start_task(self, task_id: str, goal: str) -> TaskContext:
        self.current_context = TaskContext(
            task_id=task_id,
            state=TaskState.QUEUED,
            goal=goal
        )
        return self.current_context
    
    def transition(self, new_state: TaskState, context_update: Dict[str, Any]) -> TaskContext:
        """Attempt transition; raise ValueError if invalid."""
        if not self.current_context:
            raise RuntimeError("No active task")
        
        current = self.current_context.state
        if new_state not in VALID_TRANSITIONS[current]:
            raise ValueError(f"Invalid transition: {current.name} -> {new_state.name}")
        
        # Update context
        update_dict = {
            "state": new_state,
            "updated_at": time.time(),
            "state_history": self.current_context.state_history + [current.name]
        }
        update_dict.update(context_update)
        
        # Create new immutable context
        self.current_context = TaskContext(
            **{**self.current_context.__dict__, **update_dict}
        )
        
        # Track for loop detection
        self.state_counter[new_state] = self.state_counter.get(new_state, 0) + 1
        
        return self.current_context
    
    def should_store_to_memory(self) -> bool:
        """Only store outputs with confidence >= threshold."""
        if not self.current_context:
            return False
        return self.current_context.confidence >= self.threshold
    
    def detect_loop(self, state: TaskState) -> bool:
        """Return True if same state seen 3 times consecutively."""
        return self.state_counter.get(state, 0) >= 3
    
    def to_json(self) -> str:
        return json.dumps(self.current_context.__dict__, indent=2, default=str)

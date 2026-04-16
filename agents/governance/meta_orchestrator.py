"""
Meta‑Orchestrator – loop detection, budget enforcement, cognitive load.
"""

import time
import psutil
from typing import Optional, Callable
from dataclasses import dataclass
from core.task_state import TaskStateManager, TaskState, TaskContext
from core.protocol import LLMWrapper

@dataclass
class OrchestratorConfig:
    max_agent_calls: int = 50
    max_time_seconds: int = 420
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    loop_detection_threshold: int = 3

class MetaOrchestrator:
    """Supreme controller. Decides which agents run and when."""
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.llm = LLMWrapper()
        self.state_manager = TaskStateManager()
        self.call_count = 0
        self.start_time: Optional[float] = None
    
    def execute_pipeline(self, goal: str, mode: str = "standard") -> TaskContext:
        """Main entry point for any task."""
        self.start_time = time.time()
        self.call_count = 0
        
        task_id = f"task_{int(time.time())}"
        ctx = self.state_manager.start_task(task_id, goal)
        
        try:
            # Refine goal
            ctx = self._refine_goal(ctx)
            
            # Curate expert panel
            ctx = self._curate_panel(ctx)
            
            # Research
            ctx = self._research(ctx)
            
            # Development loop (with retries)
            ctx = self._develop_and_test(ctx)
            
            # Council review
            ctx = self._council_review(ctx)
            
            # Human review (simulated here)
            ctx = self.state_manager.transition(TaskState.HUMAN_REVIEW, {})
            
            # In real system, this pauses for human input
            # For now, auto-approve if council score > 7
            if self._should_auto_approve(ctx):
                ctx = self.state_manager.transition(TaskState.APPROVED, {})
            else:
                ctx = self.state_manager.transition(TaskState.REJECTED, {})
            
            ctx = self.state_manager.transition(TaskState.DONE, {})
            return ctx
            
        except Exception as e:
            print(f"Pipeline error: {e}")
            return ctx
    
    def _check_budget(self) -> None:
        """Raise exception if budget exceeded."""
        self.call_count += 1
        if self.call_count > self.config.max_agent_calls:
            raise RuntimeError(f"Agent call budget exceeded: {self.config.max_agent_calls}")
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        if elapsed > self.config.max_time_seconds:
            raise TimeoutError(f"Task timeout: {elapsed:.1f}s > {self.config.max_time_seconds}s")
    
    def _check_cognitive_load(self) -> bool:
        """Return True if system is overloaded."""
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        return cpu > self.config.cpu_threshold or mem > self.config.memory_threshold
    
    def _refine_goal(self, ctx: TaskContext) -> TaskContext:
        self._check_budget()
        prompt = f"Refine this vague goal into a precise, actionable task: '{ctx.goal}'"
        response = self.llm.generate(prompt)
        return self.state_manager.transition(
            TaskState.REFINING,
            {"refined_goal": response["content"], "confidence": response["confidence"]}
        )
    
    def _curate_panel(self, ctx: TaskContext) -> TaskContext:
        self._check_budget()
        # Simplified: in full system, Curator agent selects
        panel = ["Researcher", "Developer", "Tester"]
        return self.state_manager.transition(TaskState.CURATING, {"expert_panel": panel})
    
    def _research(self, ctx: TaskContext) -> TaskContext:
        self._check_budget()
        from agents.pipeline.pipeline_agents import Researcher
        researcher = Researcher()
        findings = researcher.execute(ctx.refined_goal or ctx.goal)
        return self.state_manager.transition(
            TaskState.RESEARCHING,
            {"research_findings": findings["content"], "confidence": findings["confidence"]}
        )
    
    def _develop_and_test(self, ctx: TaskContext) -> TaskContext:
        from agents.pipeline.pipeline_agents import Developer, Tester
        
        max_retries = 3
        for attempt in range(max_retries):
            self._check_budget()
            developer = Developer()
            code = developer.write_code(ctx.research_findings, ctx.refined_goal)
            ctx = self.state_manager.transition(TaskState.DEVELOPING, {"code_output": code["content"]})
            
            tester = Tester()
            test_result = tester.test(code["content"])
            if test_result["passed"]:
                ctx = self.state_manager.transition(TaskState.TESTING, {"test_results": test_result})
                return ctx
            else:
                if attempt == max_retries - 1:
                    raise RuntimeError("Max retries exceeded")
                # Force different approach next iteration
                ctx = self.state_manager.transition(
                    TaskState.REVISION,
                    {"retry_count": ctx.retry_count + 1}
                )
        return ctx
    
    def _council_review(self, ctx: TaskContext) -> TaskContext:
        self._check_budget()
        from agents.council.council import AetherionCouncil
        council = AetherionCouncil()
        verdict = council.deliberate(ctx.code_output, ctx.refined_goal)
        return self.state_manager.transition(
            TaskState.COUNCIL,
            {"council_verdict": verdict, "confidence": verdict.get("score", 0.5)}
        )
    
    def _should_auto_approve(self, ctx: TaskContext) -> bool:
        if not ctx.council_verdict:
            return False
        return ctx.council_verdict.get("score", 0) >= 0.7

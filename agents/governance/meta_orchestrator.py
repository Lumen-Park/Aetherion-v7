"""
Meta-Orchestrator – Supreme Controller of Aetherion v3.
Coordinates all agents, enforces state transitions, budget limits,
cognitive load checks, and integrates the full institutional pipeline.

This is the brain of the operation. Treat it with respect.
"""

import time
import json
import psutil
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

from core.protocol import LLMWrapper, AgentMessage, Priority
from core.task_state import TaskStateManager, TaskState, TaskContext
from core.memory import KnowledgeGraph
from utils.logger import AetherionLogger
from utils.sandbox import SandboxExecutor


@dataclass
class OrchestratorConfig:
    """Runtime constraints to prevent runaway execution."""
    max_agent_calls: int = 50
    max_time_seconds: int = 420
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    loop_detection_threshold: int = 3
    confidence_gate: float = 0.45
    council_score_threshold: float = 0.50


class PipelineMode(Enum):
    STANDARD = "standard"           # Goal → Research → Code → Test → Council
    RESEARCH_ONLY = "research"      # Deep research without code
    CODE_ONLY = "code"              # Skip research, just code
    INVENTION = "invention"         # Full invention pipeline
    MISSION = "mission"             # Open-source issue solving


class MetaOrchestrator:
    """
    Supreme Controller.
    
    Responsibilities:
    - Parse user intent and select pipeline mode
    - Enforce state transitions via TaskStateManager
    - Manage agent call budget and timeouts
    - Monitor system load and pause if necessary
    - Integrate Curator, Pipeline Agents, Council, Memory
    - Handle retries with forced strategy changes
    - Log all activity for post-mortem analysis
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.llm = LLMWrapper()
        self.state_manager = TaskStateManager(confidence_threshold=self.config.confidence_gate)
        self.knowledge_graph = KnowledgeGraph()
        self.logger = AetherionLogger()
        self.sandbox = SandboxExecutor()
        
        # Runtime tracking
        self.call_count = 0
        self.start_time: Optional[float] = None
        self.current_context: Optional[TaskContext] = None
        
        # Lazy imports to avoid circular dependencies
        self._pipeline_agents = None
        self._council = None
        self._curator = None
    
    def _get_pipeline_agents(self):
        if self._pipeline_agents is None:
            from agents.pipeline.pipeline_agents import (
                Researcher, Developer, Partner, Tester, Reporter,
                Scout, Synthesizer, Presenter, GoalRefiner, DocumentationAgent
            )
            self._pipeline_agents = {
                'researcher': Researcher(),
                'developer': Developer(),
                'partner': Partner(),
                'tester': Tester(),
                'reporter': Reporter(),
                'scout': Scout(),
                'synthesizer': Synthesizer(),
                'presenter': Presenter(),
                'goal_refiner': GoalRefiner(),
                'documentation': DocumentationAgent()
            }
        return self._pipeline_agents
    
    def _get_council(self):
        if self._council is None:
            from agents.council.council import AetherionCouncil
            self._council = AetherionCouncil()
        return self._council
    
    def _get_curator(self):
        if self._curator is None:
            from agents.governance.curator import Curator
            self._curator = Curator()
        return self._curator
    
    # =========================================================================
    # Budget and Load Management
    # =========================================================================
    
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
    
    def _wait_for_resources(self) -> None:
        """Block until system load drops below threshold."""
        while self._check_cognitive_load():
            self.logger.info("Cognitive load high, pausing...", 
                             cpu=psutil.cpu_percent(), 
                             mem=psutil.virtual_memory().percent)
            time.sleep(2)
    
    # =========================================================================
    # Intent Classification
    # =========================================================================
    
    def _classify_intent(self, goal: str) -> PipelineMode:
        """Determine which pipeline mode to use based on user input."""
        goal_lower = goal.lower()
        
        invention_keywords = ["invent", "create a new", "design a novel", "blueprint", "patent"]
        if any(kw in goal_lower for kw in invention_keywords):
            return PipelineMode.INVENTION
        
        research_keywords = ["research", "analyze", "summarize", "explain", "what is", "how does"]
        if any(kw in goal_lower for kw in research_keywords) and "code" not in goal_lower:
            return PipelineMode.RESEARCH_ONLY
        
        mission_keywords = ["fix issue", "solve issue", "github", "open source", "bug"]
        if any(kw in goal_lower for kw in mission_keywords):
            return PipelineMode.MISSION
        
        code_keywords = ["write", "code", "function", "class", "script", "program", "implement"]
        if any(kw in goal_lower for kw in code_keywords):
            return PipelineMode.CODE_ONLY
        
        return PipelineMode.STANDARD
    
    # =========================================================================
    # Main Entry Point
    # =========================================================================
    
    def execute(self, goal: str, mode: Optional[str] = None) -> TaskContext:
        """
        Main entry point for any task.
        
        Args:
            goal: User's request
            mode: Override pipeline mode ('standard', 'research', 'code', 'invent', 'mission')
        
        Returns:
            TaskContext with complete execution history
        """
        self.start_time = time.time()
        self.call_count = 0
        
        task_id = f"task_{int(self.start_time)}"
        self.current_context = self.state_manager.start_task(task_id, goal)
        
        self.logger.info("Task started", task_id=task_id, goal=goal, mode=mode)
        
        try:
            # Determine pipeline mode
            pipeline_mode = PipelineMode(mode) if mode else self._classify_intent(goal)
            self.logger.info("Pipeline mode selected", mode=pipeline_mode.value)
            
            # Execute the appropriate pipeline
            if pipeline_mode == PipelineMode.INVENTION:
                return self._execute_invention_pipeline()
            elif pipeline_mode == PipelineMode.MISSION:
                return self._execute_mission_pipeline()
            else:
                return self._execute_standard_pipeline(pipeline_mode)
                
        except Exception as e:
            self.logger.error("Pipeline execution failed", error=str(e), task_id=task_id)
            self.current_context = self.state_manager.transition(
                TaskState.REJECTED,
                {"error": str(e)}
            )
            return self.current_context
    
    # =========================================================================
    # Standard Pipeline (Research + Development + Council)
    # =========================================================================
    
    def _execute_standard_pipeline(self, mode: PipelineMode) -> TaskContext:
        """Execute the full standard pipeline."""
        self._wait_for_resources()
        
        # Phase 1: Goal Refinement
        ctx = self._refine_goal()
        
        # Phase 2: Curate Expert Panel
        ctx = self._curate_panel()
        
        # Phase 3: Research (skip if CODE_ONLY)
        if mode != PipelineMode.CODE_ONLY:
            ctx = self._research()
        
        # Phase 4: Development & Testing Loop
        if mode != PipelineMode.RESEARCH_ONLY:
            ctx = self._develop_and_test()
        
        # Phase 5: Council Review
        ctx = self._council_review()
        
        # Phase 6: Human Review Simulation
        ctx = self.state_manager.transition(TaskState.HUMAN_REVIEW, {})
        
        # Phase 7: Final Decision
        if self._should_auto_approve():
            ctx = self.state_manager.transition(TaskState.APPROVED, {})
            self._store_successful_output(ctx)
        else:
            ctx = self.state_manager.transition(TaskState.REJECTED, {})
            self._log_rejection(ctx)
        
        ctx = self.state_manager.transition(TaskState.DONE, {})
        self._generate_report(ctx)
        
        self.logger.info("Pipeline complete", 
                         task_id=ctx.task_id, 
                         final_state=ctx.state.name,
                         confidence=ctx.confidence)
        
        return ctx
    
    # -------------------------------------------------------------------------
    # Phase 1: Goal Refinement
    # -------------------------------------------------------------------------
    
    def _refine_goal(self) -> TaskContext:
        """Refine vague user input into precise task."""
        self._check_budget()
        self._wait_for_resources()
        
        agents = self._get_pipeline_agents()
        refiner = agents['goal_refiner']
        
        refined = refiner.refine(self.current_context.goal)
        
        ctx = self.state_manager.transition(
            TaskState.REFINING,
            {
                "refined_goal": refined["content"],
                "confidence": refined["confidence"]
            }
        )
        self.logger.debug("Goal refined", refined=ctx.refined_goal)
        return ctx
    
    # -------------------------------------------------------------------------
    # Phase 2: Curate Expert Panel
    # -------------------------------------------------------------------------
    
    def _curate_panel(self) -> TaskContext:
        """Select minimal viable expert panel."""
        self._check_budget()
        self._wait_for_resources()
        
        curator = self._get_curator()
        goal = self.current_context.refined_goal or self.current_context.goal
        
        # Get relevant context from knowledge graph
        past_context = self.knowledge_graph.get_relevant_context(goal)
        
        experts = curator.select_experts(goal, past_context, max_experts=5)
        
        ctx = self.state_manager.transition(
            TaskState.CURATING,
            {"expert_panel": experts}
        )
        self.logger.debug("Expert panel selected", experts=experts)
        return ctx
    
    # -------------------------------------------------------------------------
    # Phase 3: Research
    # -------------------------------------------------------------------------
    
    def _research(self) -> TaskContext:
        """Conduct research using selected experts."""
        self._check_budget()
        self._wait_for_resources()
        
        agents = self._get_pipeline_agents()
        researcher = agents['researcher']
        synthesizer = agents['synthesizer']
        
        goal = self.current_context.refined_goal or self.current_context.goal
        experts = self.current_context.expert_panel
        
        # Gather individual expert analyses
        from agents.colleges.all_colleges import get_agent
        expert_findings = {}
        
        for expert_name in experts:
            agent = get_agent(expert_name)
            if agent:
                analysis = agent.analyze(goal)
                expert_findings[expert_name] = analysis
        
        # Also run primary researcher
        primary_research = researcher.execute(goal)
        
        # Synthesize all findings
        synthesis = synthesizer.synthesize(
            primary_research["content"],
            expert_findings,
            goal
        )
        
        ctx = self.state_manager.transition(
            TaskState.RESEARCHING,
            {
                "research_findings": synthesis["content"],
                "confidence": synthesis["confidence"],
                "expert_contributions": expert_findings
            }
        )
        self.logger.debug("Research complete", confidence=ctx.confidence)
        return ctx
    
    # -------------------------------------------------------------------------
    # Phase 4: Development & Testing Loop
    # -------------------------------------------------------------------------
    
    def _develop_and_test(self) -> TaskContext:
        """Development loop with forced strategy changes on retry."""
        agents = self._get_pipeline_agents()
        developer = agents['developer']
        partner = agents['partner']
        tester = agents['tester']
        
        max_retries = 3
        retry_count = 0
        last_strategy = None
        
        research = self.current_context.research_findings or ""
        goal = self.current_context.refined_goal or self.current_context.goal
        
        while retry_count < max_retries:
            self._check_budget()
            self._wait_for_resources()
            
            # Force different strategy each retry
            strategy = f"approach_{retry_count + 1}"
            if last_strategy:
                strategy = f"different_from_{last_strategy}"
            
            # Developer writes code
            code_result = developer.write_code(research, goal, strategy_hint=strategy)
            ctx = self.state_manager.transition(
                TaskState.DEVELOPING,
                {"code_output": code_result["content"]}
            )
            
            # Partner reviews
            review = partner.review(code_result["content"], goal)
            if review["requires_changes"]:
                # Partner rejected, try again with feedback
                research = f"{research}\n\nPartner feedback: {review['feedback']}"
                retry_count += 1
                last_strategy = strategy
                continue
            
            ctx = self.state_manager.transition(
                TaskState.REVIEWING,
                {"review_feedback": review["feedback"]}
            )
            
            # Tester executes (in sandbox if possible)
            test_result = self._run_tests(code_result["content"])
            ctx = self.state_manager.transition(
                TaskState.TESTING,
                {"test_results": test_result}
            )
            
            if test_result["passed"]:
                self.logger.debug("Tests passed", attempt=retry_count+1)
                return ctx
            
            # Tests failed, get debugger involved
            if retry_count < max_retries - 1:
                from agents.pipeline.pipeline_agents import Debugger
                debugger = Debugger()
                fix_result = debugger.fix(
                    code_result["content"],
                    test_result["errors"],
                    research
                )
                code_result["content"] = fix_result["content"]
                research = f"{research}\n\nDebugger analysis: {fix_result['analysis']}"
            
            retry_count += 1
            last_strategy = strategy
        
        raise RuntimeError(f"Development failed after {max_retries} attempts")
    
    def _run_tests(self, code: str) -> Dict[str, Any]:
        """Execute tests, preferably in sandbox."""
        # First, let Tester agent analyze
        agents = self._get_pipeline_agents()
        tester = agents['tester']
        analysis = tester.analyze(code)
        
        # If code is simple and safe, run in sandbox
        if self._is_safe_for_sandbox(code):
            sandbox_result = self.sandbox.run(code)
            return {
                "passed": sandbox_result["passed"],
                "errors": sandbox_result["stderr"],
                "analysis": analysis["content"],
                "sandbox_output": sandbox_result["stdout"]
            }
        else:
            # Rely on Tester's analysis only
            return {
                "passed": analysis["passed"],
                "errors": analysis.get("issues", ""),
                "analysis": analysis["content"]
            }
    
    def _is_safe_for_sandbox(self, code: str) -> bool:
        """Quick safety check before sandbox execution."""
        dangerous = ["os.system", "subprocess", "eval", "exec", "__import__", 
                     "open(", "file(", "input(", "requests.", "socket."]
        code_lower = code.lower()
        return not any(d in code_lower for d in dangerous)
    
    # -------------------------------------------------------------------------
    # Phase 5: Council Review
    # -------------------------------------------------------------------------
    
    def _council_review(self) -> TaskContext:
        """Submit output to the 7-judge Council."""
        self._check_budget()
        self._wait_for_resources()
        
        council = self._get_council()
        
        output = self.current_context.code_output or self.current_context.research_findings
        goal = self.current_context.refined_goal or self.current_context.goal
        
        # Run pre-council pipeline first
        ctx = self._run_pre_council_pipeline(output)
        sanitized_output = ctx.__dict__.get("sanitized_output", output)
        
        verdict = council.deliberate(sanitized_output, goal)
        
        ctx = self.state_manager.transition(
            TaskState.COUNCIL,
            {
                "council_verdict": verdict,
                "confidence": verdict.get("score", 0.5)
            }
        )
        self.logger.debug("Council verdict", verdict=verdict["verdict"], score=verdict.get("score"))
        return ctx
    
    def _run_pre_council_pipeline(self, output: str) -> TaskContext:
        """Execute Sanitizer → Forensic → Edge-Case pipeline."""
        from agents.council.council import SanitizerAgent, ForensicAnalyst, EdgeCaseGenerator
        
        ctx = self.current_context
        
        # Sanitize
        sanitizer = SanitizerAgent()
        sanitized = sanitizer.clean(output)
        ctx = self.state_manager.transition(
            TaskState.SANITIZING,
            {"sanitized_output": sanitized}
        )
        
        # Forensic check
        forensic = ForensicAnalyst()
        forensic_report = forensic.analyze(sanitized)
        ctx = self.state_manager.transition(
            TaskState.FORENSICS,
            {"forensic_report": forensic_report}
        )
        
        # Edge cases
        edge_gen = EdgeCaseGenerator()
        edge_cases = edge_gen.generate(sanitized)
        ctx = self.state_manager.transition(
            TaskState.EDGE_CASES,
            {"edge_cases": edge_cases}
        )
        
        return ctx
    
    # -------------------------------------------------------------------------
    # Phase 6-7: Human Review & Finalization
    # -------------------------------------------------------------------------
    def _should_auto_approve(self) -> bool:
        """Determine if output can be auto-approved (for testing only)."""
        verdict = self.current_context.council_verdict
        if not verdict:
            return False
        
        # Security veto = automatic rejection
        for vote in verdict.get("votes", []):
            if vote["agent"] == "Security" and vote["verdict"] == "reject":
                return False
        
        score = verdict.get("score", 0)
        return score >= self.config.council_score_threshold
    
    def _store_successful_output(self, ctx: TaskContext) -> None:
        """Store validated output in knowledge graph."""
        if self.state_manager.should_store_to_memory():
            key = f"task:{ctx.task_id}:{ctx.refined_goal[:50]}"
            value = {
                "goal": ctx.goal,
                "refined_goal": ctx.refined_goal,
                "output": ctx.code_output or ctx.research_findings,
                "council_score": ctx.council_verdict.get("score") if ctx.council_verdict else None
            }
            self.knowledge_graph.store(
                key=key,
                value=value,
                confidence=ctx.confidence,
                source="MetaOrchestrator"
            )
            self.logger.debug("Output stored in knowledge graph", key=key)
    
    def _log_rejection(self, ctx: TaskContext) -> None:
        """Log rejection for future pattern learning."""
        reason = "Council rejection"
        if ctx.council_verdict:
            reason = ctx.council_verdict.get("reason", reason)
        
        self.knowledge_graph.archivist.log_rejection(
            task_id=ctx.task_id,
            reason=reason,
            pattern=f"rejection_pattern_{int(time.time())}"
        )
    
    def _generate_report(self, ctx: TaskContext) -> None:
        """Generate final markdown report."""
        agents = self._get_pipeline_agents()
        reporter = agents['reporter']
        doc_agent = agents['documentation']
        
        report = reporter.generate(ctx)
        docs = doc_agent.generate(ctx)
        
        # Save to filesystem
        import os
        os.makedirs("./reports", exist_ok=True)
        report_path = f"./reports/{ctx.task_id}_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        self.logger.debug("Report generated", path=report_path)
    
    # =========================================================================
    # Invention Pipeline (Delegated)
    # =========================================================================
    
    def _execute_invention_pipeline(self) -> TaskContext:
        """Execute full invention pipeline."""
        from missions.invention_pipeline import InventionPipeline
        
        pipeline = InventionPipeline()
        latex_path = pipeline.run(self.current_context.goal)
        
        ctx = self.state_manager.transition(
            TaskState.APPROVED,
            {"invention_blueprint": latex_path}
        )
        ctx = self.state_manager.transition(TaskState.DONE, {})
        return ctx
    
    # =========================================================================
    # Mission Pipeline (Open Source)
    # =========================================================================
    
    def _execute_mission_pipeline(self) -> TaskContext:
        """Scout, solve, and prepare git payload for open source issues."""
        from missions.mission_agent import ScoutAgent, FilterAgent, SelectorAgent, GitPayloadBuilder
        
        # Scout
        scout = ScoutAgent()
        issues = scout.search_github_issues(self.current_context.goal, limit=5)
        
        # Filter
        filter_agent = FilterAgent()
        filtered = filter_agent.filter_issues(issues)
        
        # Select
        selector = SelectorAgent()
        selected = selector.select_best(filtered)
        
        if not selected:
            raise RuntimeError("No suitable issues found")
        
        # Solve using standard pipeline (but with issue context)
        self.current_context.goal = f"Fix GitHub issue: {selected['title']}\n\n{selected.get('body', '')}"
        ctx = self._execute_standard_pipeline(PipelineMode.STANDARD)
        
        if ctx.state == TaskState.APPROVED:
            # Build git payload
            builder = GitPayloadBuilder()
            payload = builder.build_payload(
                selected,
                ctx.code_output,
                ctx.research_findings or ""
            )
            ctx = self.state_manager.transition(
                TaskState.HUMAN_REVIEW,
                {"git_payload": payload}
            )
        
        return ctx
    
    # =========================================================================
    # Self-Improvement Interface
    # =========================================================================
    
    def audit_and_improve(self) -> List[Dict]:
        """
        Run self-improvement cycle on all agent files.
        Returns list of proposals awaiting human approval.
        """
        from agents.improvement.self_improve import CodeAuditAgent, RefactorArchitect, IntegrationValidator
        
        proposals = []
        agent_files = self._find_agent_files()
        
        for file_path in agent_files:
            auditor = CodeAuditAgent()
            report = auditor.audit(file_path)
            
            if report.issues and report.confidence > 0.6:
                architect = RefactorArchitect()
                proposal = architect.propose_changes(report)
                
                validator = IntegrationValidator()
                validation = validator.validate(proposal)
                
                if validation.get("passed"):
                    # Save for human review
                    proposal_path = self._save_improvement_proposal(proposal, file_path)
                    proposals.append({
                        "file": file_path,
                        "proposal_path": proposal_path,
                        "issues": report.issues
                    })
        
        return proposals
    
    def _find_agent_files(self) -> List[str]:
        """Find all agent Python files."""
        import os
        agent_files = []
        base_dir = "./agents"
        if os.path.exists(base_dir):
            for root, _, files in os.walk(base_dir):
                for f in files:
                    if f.endswith('.py') and not f.startswith('__'):
                        agent_files.append(os.path.join(root, f))
        return agent_files
    
    def _save_improvement_proposal(self, proposal, original_file: str) -> str:
        """Save proposal for human review."""
        import os
        os.makedirs("./proposed_improvements", exist_ok=True)
        
        timestamp = int(time.time())
        proposal_file = f"./proposed_improvements/{timestamp}_{os.path.basename(original_file)}.json"
        
        with open(proposal_file, 'w') as f:
            json.dump({
                "original_file": original_file,
                "diff": proposal.diff,
                "reasoning": proposal.reasoning,
                "timestamp": timestamp
            }, f, indent=2)
        
        return proposal_file

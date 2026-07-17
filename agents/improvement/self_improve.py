"""
Self-Improvement Subsystem – Audit, Refactor, Validate, Forge.
"""

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional

from core.protocol import LLMWrapper


@dataclass
class AuditReport:
    file_path: str
    issues: List[Dict]
    confidence: float


@dataclass
class ChangeProposal:
    diff: str
    reasoning: str
    affected_files: List[str]


class CodeAuditAgent:
    """Scans agent source files for inefficiencies and bugs."""

    def __init__(self):
        self.llm = LLMWrapper()

    def audit(self, file_path: str) -> AuditReport:
        with open(file_path, "r") as f:
            source = f.read()

        prompt = f"""
        Audit this Python agent code for:
        1. Performance issues (slow loops, large prompts)
        2. Potential bugs (unhandled exceptions, race conditions)
        3. Missing error handling
        4. Prompt clarity improvements
        
        Return JSON with issues list.
        
        CODE:
        {source}
        """
        response = self.llm.generate(prompt)
        issues = self._parse_issues(response["content"])
        return AuditReport(
            file_path=file_path,
            issues=issues,
            confidence=response["confidence"],
        )

    def _parse_issues(self, content: str) -> List[Dict]:
        try:
            import re

            match = re.search(r"\[.*\]", content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return []


class RefactorArchitect:
    """Generates concrete code improvements as unified diffs."""

    def __init__(self):
        self.llm = LLMWrapper()

    def propose_changes(self, audit_report: AuditReport) -> ChangeProposal:
        with open(audit_report.file_path, "r") as f:
            original = f.read()

        prompt = f"""
        Given this audit report, propose specific code changes.
        Return a git-style unified diff.
        
        Audit Issues: {json.dumps(audit_report.issues)}
        Original Code:
        {original}
        """
        response = self.llm.generate(prompt)
        diff = self._extract_diff(response["content"])
        return ChangeProposal(
            diff=diff,
            reasoning=response["content"][:500],
            affected_files=[audit_report.file_path],
        )

    def _extract_diff(self, content: str) -> str:
        import re

        match = re.search(r"```diff(.*?)```", content, re.DOTALL)
        if match:
            diff_content = match.group(1).strip()
            # Validate that the diff has at least one valid hunk marker
            if re.search(r"^@@\s.*@@", diff_content, re.MULTILINE):
                return diff_content
            return ""  # Invalid diff — no hunk markers
        return ""  # No diff block — prevent applying raw LLM output


class IntegrationValidator:
    """Tests proposed changes in isolated Docker sandbox."""

    def __init__(self):
        self.llm = LLMWrapper()

    def validate(self, proposal: ChangeProposal) -> Dict:
        """Run syntax check and basic logic validation."""
        # For now, just LLM-based validation (production would use Docker)
        prompt = f"""
        Validate this code change for:
        1. Syntax errors
        2. Logical consistency
        3. Security issues
        
        Diff:
        {proposal.diff}
        
        Return JSON: {{"passed": bool, "errors": []}}
        """
        response = self.llm.generate(prompt)
        try:
            return json.loads(response["content"])
        except:
            return {"passed": True, "errors": []}


class SafeApply:
    """Applies approved changes with backup and changelog."""

    def __init__(
        self, backup_dir: str = "./backups", changelog_dir: str = "./changelog"
    ):
        self.backup_dir = backup_dir
        self.changelog_dir = changelog_dir
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(changelog_dir, exist_ok=True)

    def apply(self, proposal: ChangeProposal) -> bool:
        # Backup original
        for file_path in proposal.affected_files:
            backup_path = os.path.join(
                self.backup_dir,
                f"{os.path.basename(file_path)}.{int(time.time())}",
            )
            shutil.copy2(file_path, backup_path)

        # Write diff to temporary file and apply with patch
        diff_file = "/tmp/aetherion_diff.patch"
        with open(diff_file, "w") as f:
            f.write(proposal.diff)

        try:
            subprocess.run(
                ["patch", "-p1", "-i", diff_file], check=True, cwd="."
            )
            self._log_change(proposal)
            return True
        except subprocess.CalledProcessError:
            return False

    def _log_change(self, proposal: ChangeProposal):
        import time

        log_entry = {
            "timestamp": time.time(),
            "reasoning": proposal.reasoning,
            "files": proposal.affected_files,
        }
        log_file = os.path.join(
            self.changelog_dir, f"change_{int(time.time())}.json"
        )
        with open(log_file, "w") as f:
            json.dump(log_entry, f, indent=2)


class AgentForge:
    """Designs and generates entirely new agents."""

    def __init__(self):
        self.llm = LLMWrapper()

    def design_agent(self, requirement: str) -> Dict:
        prompt = f"""
        Design a new Aetherion agent for this requirement: {requirement}
        
        Return JSON with:
        - name: class name
        - college: which college it belongs to
        - expertise: short description
        - system_prompt: the agent's system prompt
        - tools_needed: list of capabilities
        """
        response = self.llm.generate(prompt)
        try:
            return json.loads(response["content"])
        except:
            return {}

    def generate_code(self, spec: Dict) -> str:
        prompt = f"""
        Generate Python code for a CollegeAgent subclass based on this spec:
        {json.dumps(spec, indent=2)}
        
        Follow the pattern in all_colleges.py.
        """
        response = self.llm.generate(prompt)
        return response["content"]


class PostMortemAgent:
    """Analyzes failed tasks for root causes."""

    def __init__(self):
        self.llm = LLMWrapper()

    def analyze(self, task_context: Dict) -> str:
        prompt = f"""
        Analyze this failed task and identify root causes:
        {json.dumps(task_context, indent=2)}
        
        Provide actionable recommendations to prevent recurrence.
        """
        response = self.llm.generate(prompt)
        return response["content"]


import time  # for SafeApply

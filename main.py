#!/usr/bin/env python3
"""⚡ AETHERION v3.1 — Autonomous AI Research Institution"""

import argparse
import sys
import time
from agents.governance.meta_orchestrator import MetaOrchestrator
from agents.interfaces.interfaces import VoiceInterface
from mission.invention_pipeline import InventionPipeline
from mission.mission_agent import ScoutAgent, FilterAgent, SelectorAgent, GitPayloadBuilder
from agents.pipeline.pipeline_agents import Researcher, Developer, Tester
from agents.council.council import AetherionCouncil
from utils.logger import AetherionLogger

logger = AetherionLogger()


def chat_mode():
    print("💬 Aetherion Chat Mode — talk to Aetherion Prime")
    orchestrator = MetaOrchestrator()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = orchestrator.llm.generate(user_input, system="You are Aetherion Prime.")
        print(f"\nAetherion: {response['content']}")


def voice_mode():
    try:
        voice = VoiceInterface()
        def callback(text):
            orch = MetaOrchestrator()
            return orch.llm.generate(text, system="You are Aetherion Prime.")['content']
        voice.chat_loop(callback)
    except ImportError as e:
        print(f"Voice mode unavailable: {e}")


def pipeline_mode(goal: str):
    logger.info("Starting pipeline", goal=goal)
    orchestrator = MetaOrchestrator()
    ctx = orchestrator.execute(goal)
    logger.info("Pipeline complete", state=ctx.state.name, task_id=ctx.task_id)
    print(f"\n✅ Task completed: {ctx.state.name}")
    if ctx.council_verdict:
        print(f"Council: {ctx.council_verdict.get('verdict')} (score: {ctx.council_verdict.get('score', 0):.2f})")
    if ctx.state == TaskState.HUMAN_REVIEW:
        print("\n⚠️ Task is awaiting human review. Use --override to approve/reject.")


def override_mode(task_id: str, operator: str, reason: str):
    """Apply human override to a rejected task."""
    orchestrator = MetaOrchestrator()
    success = orchestrator.accept_override(task_id, operator, reason)
    if success:
        print(f"✅ Override accepted for task {task_id}")
    else:
        print(f"❌ Override failed for task {task_id}")
        sys.exit(1)


def invention_mode(idea: str):
    logger.info("Starting invention pipeline", idea=idea)
    pipeline = InventionPipeline()
    latex_path = pipeline.run(idea)
    print(f"📄 Invention blueprint generated: {latex_path}")


def mission_mode():
    print("🔍 Mission Mode — scouting open issues...")
    scout = ScoutAgent()
    issues = scout.search_github_issues("good first issue", limit=5)
    if not issues:
        print("No issues found.")
        return

    filtered = FilterAgent().filter_issues(issues)
    selected = SelectorAgent().select_best(filtered)
    if not selected:
        print("No suitable issues.")
        return

    print(f"Selected: {selected['title']} - {selected['url']}")
    researcher = Researcher()
    findings = researcher.execute(selected['title'] + "\n" + selected.get('body', ''))
    developer = Developer()
    code = developer.write_code(findings['content'], selected['title'])
    council = AetherionCouncil()
    verdict = council.deliberate(code['content'], selected['title'])

    if verdict['verdict'] == 'APPROVED':
        builder = GitPayloadBuilder()
        payload = builder.build_payload(selected, code['content'], findings['content'])
        print(f"✅ Solution ready. Review git payload at ./git_payloads/")
    else:
        print(f"❌ Solution rejected by Council: {verdict}")


def preflight_check():
    """Verify all dependencies."""
    import subprocess
    import os
    from core.protocol import LLMWrapper
    from chromadb.config import Settings

    results = {}
    critical_fail = False

    def record(name, status, message):
        nonlocal critical_fail
        symbol = {"PASS": "✅", "DEGRADED": "🟡", "FAIL": "❌", "MISSING": "❓"}.get(status, "?")
        print(f"  {symbol} {status}: {message}\n")
        if status in ("FAIL", "MISSING"):
            critical_fail = True

    print("=== AETHERION PREFLIGHT CHECK ===\n")
    wrapper = LLMWrapper()
    if not wrapper.available:
        record("Ollama", "FAIL", "Ollama not available")
    else:
        start = time.time()
        wrapper.generate("Hello", system="Respond with 'OK' only")
        latency = time.time() - start
        if latency > 10.0:
            record("Ollama", "DEGRADED", f"Slow ({latency:.1f}s). Tasks may exceed 420s timeout.")
        else:
            record("Ollama", "PASS", f"Responsive ({latency:.1f}s)")

        try:
            available = [m.model for m in wrapper.client.list().models]
            required = [os.getenv("OLLAMA_MODEL", "llama3"), os.getenv("OLLAMA_VISION_MODEL", "llava")]
            missing = [m for m in required if not any(m in a for a in available)]
            if missing:
                record("Ollama Models", "FAIL", f"Missing: {missing}")
            else:
                record("Ollama Models", "PASS", "All required models present")
        except Exception as e:
            record("Ollama Models", "FAIL", str(e))

    # Docker check
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
        record("Docker", "PASS", "Docker installed and running")
    except:
        record("Docker", "FAIL", "Docker not available")

    # ChromaDB check
    try:
        import chromadb
        chromadb.Client(Settings(anonymized_telemetry=False)).heartbeat()
        record("ChromaDB", "PASS", "Operational")
    except:
        record("ChromaDB", "FAIL", "Not available")

    return critical_fail


def main():
    parser = argparse.ArgumentParser(description="⚡ AETHERION v3.1 – Autonomous AI Research Institution")
    parser.add_argument("--mode", choices=["chat", "voice", "pipeline", "invent", "mission"], default="chat")
    parser.add_argument("--check", action="store_true", help="Run preflight dependency checks")
    parser.add_argument("--override", nargs=3, metavar=("TASK_ID", "OPERATOR", "REASON"), help="Apply human override")
    parser.add_argument("goal", nargs="?", help="Task description for pipeline/invent modes")
    args = parser.parse_args()

    if args.check:
        failed = preflight_check()
        sys.exit(1 if failed else 0)

    if args.override:
        from core.task_state import TaskState
        override_mode(*args.override)
        return

    print("⚡ AETHERION v3.1 — The Autonomous AI Research Institution")
    print("70 agents · 12 colleges · 7-judge Council")

    if args.mode == "chat":
        chat_mode()
    elif args.mode == "voice":
        voice_mode()
    elif args.mode == "pipeline":
        if not args.goal:
            print("Error: goal required")
            sys.exit(1)
        pipeline_mode(args.goal)
    elif args.mode == "invent":
        if not args.goal:
            print("Error: idea required")
            sys.exit(1)
        invention_mode(args.goal)
    elif args.mode == "mission":
        mission_mode()


if __name__ == "__main__":
    from core.task_state import TaskState
    main()

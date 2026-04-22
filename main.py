#!/usr/bin/env python3
"""
⚡ AETHERION v3.2 — Autonomous AI Research Institution
"""

import argparse
import sys
import time
import os
import random
import json
from agents.governance.meta_orchestrator import MetaOrchestrator
from agents.interfaces.interfaces import VoiceInterface, CronScheduler
from mission.invention_pipeline import InventionPipeline
from mission.mission_agent import ScoutAgent, FilterAgent, SelectorAgent, GitPayloadBuilder
from agents.pipeline.pipeline_agents import Researcher, Developer, Tester, Reporter
from agents.council.council import AetherionCouncil
from utils.logger import AetherionLogger
from core.task_state import TaskState

logger = AetherionLogger()


def chat_mode():
    print("💬 Aetherion Chat Mode — talk to Aetherion Prime")
    orchestrator = MetaOrchestrator()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = orchestrator.llm.generate(
            user_input,
            system="You are Aetherion Prime, the lead AI of an autonomous research institution."
        )
        print(f"\nAetherion: {response['content']}")


def voice_mode():
    try:
        voice = VoiceInterface()

        def callback(text):
            orchestrator = MetaOrchestrator()
            response = orchestrator.llm.generate(text, system="You are Aetherion Prime.")
            return response['content']

        voice.chat_loop(callback)
    except ImportError as e:
        print(f"Voice mode unavailable: {e}")


def pipeline_mode(goal: str, auth_token: str = None):
    logger.info("Starting pipeline", goal=goal)
    orchestrator = MetaOrchestrator()
    try:
        ctx = orchestrator.execute(goal, auth_token=auth_token)
    except PermissionError as e:
        print(f"❌ Access denied: {e}")
        sys.exit(1)
    logger.info("Pipeline complete", state=ctx.state.name, task_id=ctx.task_id)
    print(f"\n✅ Task completed: {ctx.state.name}")
    if ctx.council_verdict:
        print(f"Council: {ctx.council_verdict.get('verdict')} "
              f"(score: {ctx.council_verdict.get('score', 0):.2f})")


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

    filter_agent = FilterAgent()
    filtered = filter_agent.filter_issues(issues)

    selector = SelectorAgent()
    selected = selector.select_best(filtered)
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
    import subprocess
    from core.protocol import LLMWrapper
    from chromadb.config import Settings

    critical_fail = False

    def record(name, status, message):
        nonlocal critical_fail
        symbol = {"PASS": "✅", "DEGRADED": "🟡", "FAIL": "❌", "MISSING": "❓"}.get(status, "?")
        print(f"  {symbol} {status}: {message}")
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
            record("Ollama", "DEGRADED", f"Slow ({latency:.1f}s). Tasks may exceed timeout.")
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

    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
        record("Docker", "PASS", "Docker installed and running")
    except Exception:
        record("Docker", "FAIL", "Docker not available")

    try:
        import chromadb
        chromadb.Client(Settings(anonymized_telemetry=False)).heartbeat()
        record("ChromaDB", "PASS", "Operational")
    except Exception:
        record("ChromaDB", "FAIL", "Not available")

    return critical_fail


def start_autonomous_mode():
    scheduler = CronScheduler()
    reporter = Reporter()

    def daily_literature_review():
        print(f"[{time.ctime()}] Running daily literature review...")
        orch = MetaOrchestrator()
        topics = [
            "quantum machine learning",
            "large language model safety",
            "renewable energy materials",
            "CRISPR gene editing",
            "artificial general intelligence",
            "carbon capture technology",
        ]
        topic = random.choice(topics)
        goal = (
            f"Search arXiv for the latest papers on '{topic}', "
            f"read their abstracts, and produce a concise summary of key findings and trends."
        )
        ctx = orch.execute(goal, mode="pipeline")
        report = reporter.generate(ctx)
        os.makedirs("./reports", exist_ok=True)
        report_path = f"./reports/literature_review_{time.strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        print(f"[{time.ctime()}] Report saved to {report_path}")

    def hourly_check():
        print(f"[{time.ctime()}] Hourly health check...")
        orch = MetaOrchestrator()
        orch.execute("Check if there are any urgent system notifications or errors in the logs.", mode="pipeline")

    scheduler.add_daily_job("09:00", daily_literature_review)
    scheduler.add_hourly_job(hourly_check)
    scheduler.start()

    print("\n🧬 AETHERION AUTONOMOUS LAB ACTIVATED")
    print("   - Daily literature review at 09:00")
    print("   - Hourly health checks")
    print("   Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Autonomous mode stopped.")


def lab_mode(research_question: str = None):
    from agents.colleges.all_colleges import (
        PythonDataAnalystAgent, HypothesisTesterAgent, ExternalToolAgent
    )

    print("🧪 AETHERION EXPERIMENT MODE ACTIVATED\n")

    if not research_question:
        research_question = input("Enter research question: ")

    orch = MetaOrchestrator()
    reporter = Reporter()

    print("1️⃣ Formulating hypothesis...")
    hypothesis_agent = HypothesisTesterAgent(name="HypothesisTester")
    hypothesis_design = hypothesis_agent.design_experiment(research_question, ["independent", "dependent"])

    print("2️⃣ Gathering external data...")
    tool_agent = ExternalToolAgent(name="ExternalTool")
    external_data = {}
    if "weather" in research_question.lower():
        city = input("City for weather data: ") or "London"
        external_data["weather"] = tool_agent.call_tool("get_weather", city=city)

    print("3️⃣ Running data analysis...")
    analyst = PythonDataAnalystAgent(name="PythonDataAnalyst")
    analysis_code = f"""
import numpy as np
import scipy.stats as stats

control = np.random.normal(100, 15, 30)
treatment = np.random.normal(110, 15, 30)

t_stat, p_value = stats.ttest_ind(control, treatment)
print(f"T-statistic: {{t_stat:.4f}}")
print(f"P-value: {{p_value:.4f}}")
print(f"Mean difference: {{np.mean(treatment) - np.mean(control):.2f}}")
"""
    analysis_result = analyst.run_analysis(analysis_code, data=external_data)

    print("4️⃣ Evaluating hypothesis...")
    evaluation = hypothesis_agent.evaluate_results(
        research_question,
        {"external_data": external_data, "analysis_stdout": analysis_result["stdout"]},
        analysis_result["analysis"]
    )

    print("5️⃣ Submitting to Council...")
    ctx = orch.execute(
        f"Research question: {research_question}\n"
        f"Hypothesis design: {hypothesis_design}\n"
        f"Analysis results: {analysis_result}\n"
        f"Evaluation: {evaluation}\n"
        "Produce a final research conclusion.",
        mode="pipeline"
    )

    report = reporter.generate(ctx)
    os.makedirs("./reports", exist_ok=True)
    report_path = f"./reports/experiment_{time.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Experiment complete! Report saved to {report_path}")
    print(f"   Verdict: {evaluation.get('verdict', 'unknown')}")
    print(f"   Council: {ctx.council_verdict.get('verdict', 'unknown')}")


def override_mode(task_id: str, operator: str, reason: str, auth_token: str = None):
    orchestrator = MetaOrchestrator()
    success = orchestrator.accept_override(task_id, operator, reason, auth_token=auth_token)
    if success:
        print(f"✅ Override accepted for task {task_id}")
    else:
        print(f"❌ Override failed for task {task_id}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="⚡ AETHERION v3.2 – Autonomous AI Research Institution")
    parser.add_argument("--mode", choices=["chat", "voice", "pipeline", "invent", "mission", "lab"], default="chat")
    parser.add_argument("--check", action="store_true", help="Run preflight dependency checks")
    parser.add_argument("--autonomous", action="store_true", help="Run as autonomous research lab")
    parser.add_argument("--override", nargs=3, metavar=("TASK_ID", "OPERATOR", "REASON"), help="Apply human override")
    parser.add_argument("--auth-token", help="Authentication token (API key or JWT)", default=os.getenv("AETHERION_AUTH_TOKEN"))
    parser.add_argument("goal", nargs="?", help="Task description for pipeline/invent/lab modes")
    args = parser.parse_args()

    if args.check:
        failed = preflight_check()
        sys.exit(1 if failed else 0)

    if args.autonomous:
        start_autonomous_mode()
        sys.exit(0)

    if args.override:
        override_mode(*args.override, auth_token=args.auth_token)
        return

    print("""
    ⚡ AETHERION v3.2
    The Autonomous AI Research Institution
    70+ agents · 13 colleges · 7-judge Council
    """)

    if args.mode == "chat":
        chat_mode()
    elif args.mode == "voice":
        voice_mode()
    elif args.mode == "pipeline":
        if not args.goal:
            print("Error: goal required for pipeline mode")
            sys.exit(1)
        pipeline_mode(args.goal, auth_token=args.auth_token)
    elif args.mode == "invent":
        if not args.goal:
            print("Error: idea required for invention mode")
            sys.exit(1)
        invention_mode(args.goal)
    elif args.mode == "mission":
        mission_mode()
    elif args.mode == "lab":
        lab_mode(args.goal)


if __name__ == "__main__":
    main()

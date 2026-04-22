#!/usr/bin/env python3
"""
⚡ AETHERION v3 – Autonomous AI Research Institution
"""

import argparse
import sys
from agents.governance.meta_orchestrator import MetaOrchestrator
from agents.interfaces.interfaces import VoiceInterface
from mission.invention_pipeline import InventionPipeline
from utils.logger import AetherionLogger

logger = AetherionLogger()

def chat_mode():
    print("💬 Aetherion Chat Mode – talk to Aetherion Prime")
    orchestrator = MetaOrchestrator()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        # Simple chat: just use LLM directly
        response = orchestrator.llm.generate(user_input, system="You are Aetherion Prime, the lead AI of an autonomous research institution.")
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

def pipeline_mode(goal: str):
    logger.info("Starting pipeline", goal=goal)
    orchestrator = MetaOrchestrator()
    ctx = orchestrator.execute(goal)
    logger.info("Pipeline complete", state=ctx.state.name, task_id=ctx.task_id)
    print(f"\n✅ Task completed: {ctx.state.name}")
    if ctx.council_verdict:
        print(f"Council: {ctx.council_verdict.get('verdict')} (score: {ctx.council_verdict.get('score', 0):.2f})")

def invention_mode(idea: str):
    logger.info("Starting invention pipeline", idea=idea)
    pipeline = InventionPipeline()
    latex_path = pipeline.run(idea)
    print(f"📄 Invention blueprint generated: {latex_path}")

def mission_mode():
    print("🔍 Mission Mode – scouting open issues...")
    from mission.mission_agent import ScoutAgent, FilterAgent, SelectorAgent, GitPayloadBuilder
    from agents.pipeline.pipeline_agents import Researcher, Developer
    from agents.council.council import AetherionCouncil
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
    # Now solve it
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

def main():
    parser = argparse.ArgumentParser(description="⚡ AETHERION v3 – Autonomous AI Research Institution")
    parser.add_argument("--mode", choices=["chat", "voice", "pipeline", "invent", "mission"], default="chat")
    parser.add_argument("goal", nargs="?", help="Task description for pipeline/invent modes")
    args = parser.parse_args()
    
    print("""
    ⚡ AETHERION v3
    The Autonomous AI Research Institution
    67+ agents · 11 colleges · 7-judge Council
    """)
    
    if args.mode == "chat":
        chat_mode()
    elif args.mode == "voice":
        voice_mode()
    elif args.mode == "pipeline":
        if not args.goal:
            print("Error: goal required for pipeline mode")
            sys.exit(1)
        pipeline_mode(args.goal)
    elif args.mode == "invent":
        if not args.goal:
            print("Error: idea required for invention mode")
            sys.exit(1)
        invention_mode(args.goal)
    elif args.mode == "mission":
        mission_mode()

if __name__ == "__main__":
    main()

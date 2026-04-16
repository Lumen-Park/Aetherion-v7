#!/usr/bin/env python3
"""
Aetherion v3 — Autonomous AI Research Institution
"""

import argparse
import sys
from agents.governance.meta_orchestrator import MetaOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Aetherion v3")
    parser.add_argument("--mode", choices=["chat", "pipeline", "invent", "mission"], default="chat")
    parser.add_argument("goal", nargs="?", help="Task description")
    args = parser.parse_args()
    
    print("⚡ AETHERION v3 — The Institution is Open")
    
    if args.mode == "chat":
        print("Chat mode: talk directly to Aetherion Prime.")
        # Implement chat loop
    elif args.mode == "pipeline":
        if not args.goal:
            print("Error: goal required for pipeline mode")
            sys.exit(1)
        orchestrator = MetaOrchestrator()
        ctx = orchestrator.execute_pipeline(args.goal)
        print(f"\n✅ Task {ctx.task_id} completed with state: {ctx.state.name}")
        if ctx.council_verdict:
            print(f"Council verdict: {ctx.council_verdict.get('verdict')}")
    elif args.mode == "invent":
        print("Invention mode: Idea → Blueprint → LaTeX")
        # Import and run invention pipeline
    elif args.mode == "mission":
        print("Mission mode: Scout open issues → Solve → Human approval")

if __name__ == "__main__":
    main()

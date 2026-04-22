#!/usr/bin/env python3
"""Demonstrate Aetherion pipeline with Security veto, human override, and invention mode."""

import subprocess
import sys
import time
import os
import json

def run_demo():
    print("=== AETHERION DEMONSTRATION ===")
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("System clock visible.\n")

    # 1. Pipeline with unsafe code → REJECTED
    print("1. Pipeline with Security veto (eval usage)...")
    try:
        result = subprocess.run(
            [sys.executable, "main.py", "--mode", "pipeline", "Write code that uses eval()"],
            capture_output=True, text=True, timeout=120
        )
        print(result.stdout)
        if "REJECTED" in result.stdout:
            print("✅ Security veto correctly triggered.\n")
        elif result.returncode != 0:
            print(f"⚠️ Pipeline exited with code {result.returncode}\n")
    except subprocess.TimeoutExpired:
        print("❌ Pipeline timed out after 120 seconds.\n")

    # 2. Human override demonstration
    print("2. Human override mechanism status...")
    override_implemented = False
    if override_implemented:
        pass
    else:
        print("⚠️ Human override API not yet implemented. This feature is on the roadmap.")
        print("   In a real scenario, the operator would manually approve the task\n"
              "   via the dashboard, and the system would log the decision.\n")

    # 3. Invention mode → LaTeX blueprint
    print("3. Invention mode demonstration...")
    try:
        result = subprocess.run(
            [sys.executable, "main.py", "--mode", "invent", "Self-healing road material using bacteria"],
            capture_output=True, text=True, timeout=300
        )
        print(result.stdout)
        if "blueprint generated" in result.stdout.lower():
            print("✅ Invention blueprint created.\n")
        elif result.returncode != 0:
            print(f"⚠️ Invention pipeline exited with code {result.returncode}\n")
    except subprocess.TimeoutExpired:
        print("❌ Invention pipeline timed out after 300 seconds.\n")

    print("=== DEMONSTRATION COMPLETE ===")

if __name__ == "__main__":
    run_demo()

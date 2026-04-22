#!/usr/bin/env python3
"""Audit all college agents: instantiate and test a prompt. Output raw and fixed logs."""

import json
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.colleges.all_colleges import AGENT_REGISTRY, get_agent

TEST_PROMPT = "What are the key considerations for this domain?"

def attempt_fix(agent_name: str, error: str) -> bool:
    """
    Apply known fixes for specific agents. Returns True if fixed.
    Currently a deliberate stub — will be populated with actual remediation
    logic after the raw audit identifies concrete failure patterns.
    """
    return False

def audit_all_agents():
    raw_results = []
    fixed_results = []

    for name in sorted(AGENT_REGISTRY.keys()):
        print(f"Testing {name}...")
        raw_entry = {"agent": name}
        try:
            agent = get_agent(name)
            if agent is None:
                raw_entry["status"] = "FAIL"
                raw_entry["error"] = "get_agent returned None"
            else:
                response = agent.analyze(TEST_PROMPT)
                if response and response.get("assessment"):
                    raw_entry["status"] = "PASS"
                    raw_entry["response_preview"] = response["assessment"][:100]
                else:
                    raw_entry["status"] = "FAIL"
                    raw_entry["error"] = "Empty or malformed response"
        except Exception as e:
            raw_entry["status"] = "FAIL"
            raw_entry["error"] = str(e)
            raw_entry["traceback"] = traceback.format_exc()

        raw_results.append(raw_entry)

        fixed_entry = raw_entry.copy()
        if raw_entry["status"] == "FAIL":
            if attempt_fix(name, raw_entry.get("error", "")):
                try:
                    agent = get_agent(name)
                    response = agent.analyze(TEST_PROMPT)
                    if response and response.get("assessment"):
                        fixed_entry["status"] = "FIXED"
                        fixed_entry["response_preview"] = response["assessment"][:100]
                        fixed_entry["fix_applied"] = True
                except Exception:
                    pass
        fixed_results.append(fixed_entry)

    with open("agent_audit_raw.json", "w") as f:
        json.dump(raw_results, f, indent=2)
    with open("agent_audit_fixed.json", "w") as f:
        json.dump(fixed_results, f, indent=2)

    passed = sum(1 for r in fixed_results if r["status"] in ("PASS", "FIXED"))
    total = len(fixed_results)
    print(f"\nAudit complete: {passed}/{total} agents operational.")
    return passed == total

if __name__ == "__main__":
    success = audit_all_agents()
    sys.exit(0 if success else 1)

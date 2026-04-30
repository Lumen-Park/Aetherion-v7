# Architecture Overview

Aetherion is a three‑tier institutional AI system.

## Tier 1 – Governance
- **Meta‑Orchestrator** classifies user intent, enforces budgets, and coordinates tasks.
- **Curator** dynamically selects the minimal expert panel (≤5 agents).

## Tier 2 – Supreme Council
Seven judges review every output:
- **Critic, Security, Alignment, Constraint, Evaluator, Documentation, AetherionPrime**
- **Security** holds absolute veto.
- Pre‑council pipeline: Sanitizer → Forensic Analyst → Edge‑Case Generator.
- Post‑council: Juror (bias detection), Liaison (human readable verdict).

## Tier 3 – Academic Colleges
70+ domain‑expert agents across 14 colleges. Each agent runs as a Python class
or as an independent microservice via HTTP.

See [Council & Governance](council.md) for the full deliberation protocol.

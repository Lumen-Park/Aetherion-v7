# Codebase Task Proposals

## 1) Typo fix task
**Task:** Rename the `missions/` import references in `main.py` to `mission/` (or rename the package folder consistently) so module paths match the real directory.

**Why this is a typo-level fix:** The code imports `missions.invention_pipeline` and `missions.mission_agent`, while the repository directory is `mission/`. This is a naming mismatch that reads like a pluralization typo and causes runtime import failure.

## 2) Bug fix task
**Task:** Fix missing imports in mission/invention pipelines (`time` in `mission/invention_pipeline.py`; `os` and `time` in `mission/mission_agent.py`) and add a quick smoke test that exercises payload/LaTeX filename generation.

**Why this is a bug:** Both modules call `time.time()` and/or `os.makedirs(...)` without importing required modules, which will raise `NameError` during execution.

## 3) Comment/documentation discrepancy task
**Task:** Reconcile README directory docs with the real tree (e.g., README says `missions/` and many top-level folders that do not exist in this repo) or add a note that those paths are optional/generated at runtime.

**Why this is a discrepancy:** The documented structure diverges from the checked-in layout (`mission/` exists, not `missions/`; many listed directories are absent), so setup and navigation guidance are currently misleading.

## 4) Test improvement task
**Task:** Add a small test suite (e.g., `pytest`) for `TaskStateManager` transition rules, including at least one invalid transition assertion and loop detection behavior.

**Why this improves tests:** `TaskStateManager` enforces core workflow invariants, but no tests currently validate transition safety or non-reversible graph behavior.

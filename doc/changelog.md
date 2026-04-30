```markdown
# Changelog

## v3.4.0 (April 2026) – The Production‑Hardened Institution

### Added
- **Agent Microservices** – All 70+ agents can run as independent containers.
- **Constitution Editor** – GUI for customising judge prompts and thresholds.
- **Full Observability Stack** – Prometheus, Loki, Grafana, Alertmanager.
- **Tamper‑Proof Audit Logging** – Cryptographically chained and signed.
- **gVisor Sandbox** – Hardened container runtime with seccomp and egress controls.
- **GDPR/CCPA Compliance** – Export, deletion, and consent endpoints.
- **Kubernetes Deployment** – Manifest with liveness/readiness probes.
- **React Dashboard** – Full web UI with task manager, agent catalog, Council monitor.
- **Celery + Redis Task Queue** – Distributed task execution with graceful shutdown.
- **Agent Response Caching** – Redis‑backed cache for repeated agent calls.
- **Rate Limiting & Idempotency** – Production API safeguards.
- **Workspace Manager** – Multi‑tenant isolation for team deployments.

### Changed
- Council voting now supports weighted judge reputations.
- Verdict thresholds are configurable per workspace.
- Pre‑council pipeline refactored for reliability.
- Security defaults intentionally permissive for local use; hardened for production.

### Fixed
- Six critical Council bugs (mock responses, greedy regex, serialisation issues).
- Indentation and import errors in `all_colleges.py` and `meta_orchestrator.py`.
- Pipeline state transition bug (CURATING → DEVELOPING).
- Email attachment encoding and SMTP password handling.
- ChromaDB `$exists` compatibility across versions.

---

## v3.3.0 (March 2026) – Governance & Observability Foundation

### Added
- **Weighted Voting** with reputation feedback.
- **Constitution Storage** per workspace.
- **Agent Catalog API** – Enable/disable agents per workspace.
- **Task Progress Tracking** with real‑time state and estimated time remaining.
- **Loki + Grafana** integration for centralised logging.
- **Alerting Rules** for budget, failures, and resources.
- **Health Probes** for Kubernetes.

### Changed
- Metabase replaced with Grafana.
- `StrictLLMWrapper` uses Ollama tool‑calling for reliable JSON output.

---

## v3.2.0 (February 2026) – Autonomous Operation

### Added
- **Autonomous Mode** (`--autonomous`) with daily literature reviews.
- **Experiment Mode** (`--mode lab`) – hypothesis → data gathering → analysis → Council.
- **ArXivAgent** – Live academic literature search.
- **ExternalToolAgent** – Weather and stock API integration.
- **PythonDataAnalystAgent** – Sandboxed Python execution for data analysis.
- **HypothesisTesterAgent** – Statistical hypothesis evaluation.

---

## v3.1.0 (January 2026) – Governance Hardening

### Added
- **Human Override API** with tamper‑proof logging.
- **Agent Call Budget Enforcement**.
- **State Machine Loop Force‑Forward**.
- **Secure Sandbox** with seccomp and user namespaces.
- **Secrets Manager** for encrypted `.env` values.

### Fixed
- Numerous syntax and import errors from initial release.
- State machine transition validation strengthened.

---

## v3.0.0 (December 2025) – Initial Public Release

### Added
- 67+ domain‑expert agents across 11 colleges.
- 7‑judge Supreme Council with absolute Security veto.
- Pipeline: Goal → Research → Code → Test → Council.
- Web dashboard, voice, vision, email, and cron interfaces.
- Self‑improvement framework (audit → propose → human approve).


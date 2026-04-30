```markdown
# Developer Guide

## Environment Setup

```bash
git clone https://github.com/Lumen-Park/Aetherion-.git
cd Aetherion-
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Running Locally (Development)

```bash
# CLI chat mode (no Docker needed)
python main.py --mode chat

# Preflight health check
python main.py --check

# Run a pipeline task
python main.py --mode pipeline "Write a function to check if a number is prime"
```

Docker Development

```bash
docker-compose up --build   # rebuild images after code changes
```

For faster iteration, mount the local code into the container (already done via docker-compose.yml volumes for the api service).

Project Structure

See the Architecture document for the logical structure. Key source directories:

· agents/ – all agent classes, council, orchestrator, curator, pipeline agents, interfaces, and microservice support
· core/ – protocol, state machine, memory, auth, OAuth, workspace
· api/ – FastAPI backend, routers, middleware, Celery tasks
· dashboard/ – React frontend
· utils/ – sandbox, logging, secrets, audit, egress proxy
· tests/ – 84+ pytest tests

Testing

```bash
# Run all tests with coverage
pytest --cov=core --cov=agents/council --cov=agents/governance --cov-report=term

# Run a specific test file
pytest tests/test_council_security.py -v

# CI setup
# GitHub Actions runs linting, security scanning, and tests on push/PR
```

Coverage must remain ≥60%. CI fails if below.

Code Style

We use Black (line length 79) and isort:

```bash
black agents/ core/ tests/ mission/ utils/ api/ --line-length 79
isort agents/ core/ tests/ mission/ utils/ api/
```

Flake8 and Bandit run in CI; rules are relaxed for research code (see .flake8).

Adding a New Feature

1. Agent: see agents.md
2. Council Judge: add entry to AetherionCouncil.__init__ and _judge_prompt.
3. API Endpoint: add router in api/routers/, then register in api/main.py.
4. Dashboard Component: add JSX in dashboard/src/components/ and a route in App.jsx.

Always add tests before merging.

Debugging

· Check Celery worker logs: docker logs aetherion-celery-worker
· Check API logs: docker logs aetherion-api
· Structured logs are in logs/ and visible in Grafana (Loki).
· Prometheus metrics at http://localhost:8000/api/metrics

CI/CD Pipeline

The .github/workflows/main.yml file runs:

· Lint (flake8, bandit, safety)
· Tests matrix (Python 3.10–3.12, Ubuntu & macOS)
· Auto‑format (Black + isort)
· Build & Release (on version tags)
· Integration tests (manual trigger)
· Deploy to staging (manual trigger)

Contributing

See CONTRIBUTING.md for guidelines.

```

---

## `doc/observability.md`

```markdown
# Observability & Monitoring

Aetherion ships with a complete open‑source observability stack, pre‑configured
in `docker-compose.yml`.

## Metrics (Prometheus)

All metrics are exposed at `/api/metrics`. The following are available:

| Metric | Type | Description |
|--------|------|-------------|
| `aetherion_tasks_total` | Counter | Completed tasks, labelled by verdict |
| `aetherion_task_duration_seconds` | Histogram | Total pipeline execution time |
| `aetherion_council_approval_rate` | Gauge | Ratio of APPROVED verdicts |
| `aetherion_council_deliberation_seconds` | Histogram | Council deliberation time |
| `aetherion_agent_latency_seconds` | Histogram | Per‑agent response time |
| `aetherion_cpu_usage_percent` | Gauge | Current CPU usage |
| `aetherion_memory_usage_bytes` | Gauge | Current memory usage |

## Dashboards (Grafana)

Grafana is at `http://localhost:3001` (admin / admin; change immediately in production).

A pre‑built dashboard **“Aetherion – System Overview”** includes:
- CPU & memory gauges
- Task throughput (tasks/sec)
- Council approval rate gauge
- Agent latency table
- Council deliberation time

The dashboard is auto‑provisioned from `grafana/provisioning/dashboards/`.

## Centralised Logging (Loki + Promtail)

Structured JSONL logs from all services are tailed by **Promtail** and shipped
to **Loki**. Logs are queryable in Grafana via the **Explore** tab (select Loki
as the data source).

## Alerting

Prometheus alerting rules in `aetherion-alerts.yml` trigger on:
- Agent call budget exceeded
- Task failure rate spike
- Council approval rate drop below 30%
- CPU > 80% or memory > 2 GB

Notifications are sent via Slack and email through **Alertmanager** (configured
in `alertmanager.yml`).

## Health Probes

For orchestration:
- `/health/live` – liveness
- `/health/ready` – readiness (checks Ollama & ChromaDB)

Used by Kubernetes and Docker Compose health checks.
```

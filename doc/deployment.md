```markdown
# Deployment Guide

Aetherion is distributed as a self‑contained Docker stack and optionally as
Kubernetes manifests. The recommended method for most users is Docker Compose.

## Docker Compose (One‑Command Deployment)

```bash
git clone https://github.com/Lumen-Park/Aetherion-.git
cd Aetherion-
cp .env.example .env          # review and adjust settings
docker-compose up              # CPU‑only
docker-compose --profile gpu up  # GPU acceleration (NVIDIA only)
```

This starts:

· Ollama (local LLM runtime)
· ChromaDB (knowledge graph)
· Redis (Celery broker & cache)
· FastAPI (backend API)
· Celery worker
· React dashboard (served by Nginx)
· Nginx reverse proxy
· Prometheus, Loki, Grafana, Promtail, Alertmanager

The dashboard is available at http://localhost:8000.
Grafana is at http://localhost:3001 (admin / admin).

Agent Microservices (Optional)

Each domain expert can run as an independent container. Generate the services:

```bash
python scripts/generate_agent_services.py >> docker-compose.yml
docker-compose up --scale physicistagent=3
```

This enables fault isolation and independent scaling of agents.

Kubernetes

A sample deployment is provided in k8s‑deployment.yaml. It defines:

· 2 replicas of the FastAPI service
· Liveness probe: /health/live
· Readiness probe: /health/ready

Stateful services (Ollama, ChromaDB, Redis) should be run as separate
StatefulSets or external services.

Apply with:

```bash
kubectl apply -f k8s-deployment.yaml
```

Health Probes

Both deployment methods use the built‑in health endpoints:

Endpoint Purpose Success Condition
/health/live Process alive Always returns 200
/health/ready Dependencies OK 200 if Ollama & ChromaDB are reachable

Backup & Restore

Critical data directories:

· memory/ – ChromaDB knowledge graph
· audit/ – tamper‑proof logs
· workspaces/ – workspace configurations
· council_archive/ – Council verdicts

Manual backup:

```bash
tar -czf backup_$(date +%Y%m%d).tar.gz memory/ audit/ workspaces/ council_archive/
```

Automated backup script:

```bash
python scripts/backup.py
```

Restore:

```bash
python scripts/restore.py backup_20260401.tar.gz
```

Environment Variables

See .env.example for all configurable options. Critical variables:

Variable Purpose
AETHERION_REQUIRE_AUTH Enable authentication (true/false)
AETHERION_JWT_SECRET Secret for signing JWT tokens
SANDBOX_RUNTIME Container runtime (runsc or runc)
SANDBOX_NETWORK_MODE Network policy (none/allow_list/host)
AETHERION_MASTER_KEY Master password for secret encryption



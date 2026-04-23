"""
Prometheus metrics instrumentation for Aetherion.
Tracks task success, council approval, agent latency, and resource usage.
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["Metrics"])

# ---------------------------------------------------------------------------
# Task metrics
# ---------------------------------------------------------------------------
task_success_counter = Counter(
    'aetherion_tasks_total',
    'Total number of pipeline tasks executed, labelled with verdict',
    ['verdict']
)

task_duration_seconds = Histogram(
    'aetherion_task_duration_seconds',
    'Time taken to complete a complete pipeline task',
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1200]
)

# ---------------------------------------------------------------------------
# Council metrics
# ---------------------------------------------------------------------------
council_approval_rate = Gauge(
    'aetherion_council_approval_rate',
    'Current ratio of APPROVED verdicts to total verdicts'
)

council_deliberation_seconds = Histogram(
    'aetherion_council_deliberation_seconds',
    'Time taken by the Council to deliberate',
    buckets=[0.5, 1, 2, 5, 10, 20, 30, 60]
)

# ---------------------------------------------------------------------------
# Agent metrics
# ---------------------------------------------------------------------------
agent_latency_seconds = Histogram(
    'aetherion_agent_latency_seconds',
    'Latency of individual agent responses',
    ['agent_name'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 20, 30]
)

# ---------------------------------------------------------------------------
# Resource metrics
# ---------------------------------------------------------------------------
cpu_usage_percent = Gauge(
    'aetherion_cpu_usage_percent',
    'Current CPU usage percentage'
)

memory_usage_bytes = Gauge(
    'aetherion_memory_usage_bytes',
    'Current memory usage in bytes'
)

# ---------------------------------------------------------------------------
# Metrics endpoint
# ---------------------------------------------------------------------------
@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Expose Prometheus metrics."""
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")

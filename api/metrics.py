"""
Prometheus metrics instrumentation for Aetherion.
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["Metrics"])

# Task metrics
task_success_counter = Counter(
    'aetherion_tasks_total',
    'Total number of pipeline tasks executed',
    ['verdict']
)

task_duration_seconds = Histogram(
    'aetherion_task_duration_seconds',
    'Time taken to complete a pipeline task'
)

# Council metrics
council_approval_rate = Gauge(
    'aetherion_council_approval_rate',
    'Ratio of APPROVED verdicts to total verdicts'
)

council_deliberation_seconds = Histogram(
    'aetherion_council_deliberation_seconds',
    'Time taken by the Council to deliberate'
)

# Agent metrics
agent_latency_seconds = Histogram(
    'aetherion_agent_latency_seconds',
    'Latency of individual agent responses',
    ['agent_name']
)

# Resource metrics
cpu_usage_percent = Gauge(
    'aetherion_cpu_usage_percent',
    'Current CPU usage percentage'
)

memory_usage_bytes = Gauge(
    'aetherion_memory_usage_bytes',
    'Current memory usage in bytes'
)

# Endpoint to expose metrics
@router.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")

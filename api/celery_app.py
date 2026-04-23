"""
Celery application with graceful shutdown support.
"""

from celery import Celery
from celery.signals import worker_shutting_down, worker_process_shutdown
import os
import signal
import sys
import time

celery_app = Celery(
    "aetherion",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_prefetch_multiplier=1,
    task_acks_late=True,          # Re‑queue task if worker dies
    task_reject_on_worker_lost=True,  # Ensure task is retried elsewhere
)


# ---------------------------------------------------------------------------
# Graceful shutdown handling
# ---------------------------------------------------------------------------
SHUTDOWN_IN_PROGRESS = False
SHUTDOWN_GRACE_PERIOD = 30  # seconds to wait for tasks to finish

def graceful_shutdown(signum, frame):
    """Signal handler for SIGTERM/SIGINT."""
    global SHUTDOWN_IN_PROGRESS
    if not SHUTDOWN_IN_PROGRESS:
        SHUTDOWN_IN_PROGRESS = True
        print(f"\n[⚠️] Received signal {signum}. Starting graceful shutdown...")
        print(f"[⏳] Waiting {SHUTDOWN_GRACE_PERIOD}s for running tasks to save state...")
        time.sleep(SHUTDOWN_GRACE_PERIOD)
        print("[✅] Graceful shutdown complete. Exiting.")
        sys.exit(0)

# Register handlers
signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)


@worker_shutting_down.connect
def worker_shutting_down_handler(sig, how, exitcode, **kwargs):
    """Celery signal: called when worker begins shutdown."""
    print(f"[🔴] Celery worker shutting down (signal: {sig}). Saving in‑flight task states...")
    # Give tasks a moment to save
    time.sleep(5)


@worker_process_shutdown.connect
def worker_process_shutdown_handler(pid, exitcode, **kwargs):
    """Called when a worker child process exits."""
    print(f"[🛑] Worker process {pid} exited with code {exitcode}.")

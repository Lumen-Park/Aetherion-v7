from fastapi import BackgroundTasks
from collections import deque
import asyncio

task_queue = deque()
processing = False

async def process_queue():
    global processing
    processing = True
    while task_queue:
        task = task_queue.popleft()
        # Execute pipeline
        orchestrator = MetaOrchestrator()
        ctx = orchestrator.execute(task["goal"], mode=task["mode"], auth_token=task["auth_token"])
        # Store result in a database or cache for later retrieval
        # ...
        await asyncio.sleep(1)
    processing = False

@router.post("/pipeline")
async def run_pipeline(request: TaskRequest, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    # Enqueue the task
    task_id = f"task_{int(time.time())}"
    task_queue.append({"id": task_id, "goal": request.goal, "mode": request.mode, "auth_token": user.get("token")})
    if not processing:
        background_tasks.add_task(process_queue)
    return {"status": "queued", "task_id": task_id}

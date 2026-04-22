from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/deliberation")
async def deliberation_stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # In production, subscribe to a Redis pub/sub channel or internal event bus
            # For now, we'll just echo a heartbeat
            await websocket.send_json({"type": "heartbeat", "timestamp": asyncio.get_event_loop().time()})
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

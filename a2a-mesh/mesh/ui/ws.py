"""WebSocket handler for real-time UI updates."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from starlette.websockets import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class EventBus:
    """Simple pub/sub event bus for pushing events to WebSocket clients."""

    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to events. Returns a queue to read from."""
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        """Unsubscribe from events."""
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    async def publish(self, event_type: str, data: Any):
        """Publish an event to all subscribers."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass  # Drop events for slow consumers


# Global event bus
event_bus = EventBus()


async def websocket_handler(websocket: WebSocket):
    """WebSocket endpoint for real-time mesh events.

    Pushes events like:
    - agent_joined / agent_left
    - task_created / task_updated / task_completed
    - intent_pending / intent_approved / intent_rejected
    - file_changed
    - chat_message
    """
    await websocket.accept()
    queue = event_bus.subscribe()

    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        event_bus.unsubscribe(queue)

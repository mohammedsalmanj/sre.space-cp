from .interface import EventBusInterface
import json

class LocalEventBus(EventBusInterface):
    async def emit(self, topic: str, message: dict):
        print(f"EVENT_PUBLISHED: {topic} -> {json.dumps(message)}")
    
    async def subscribe(self, topics: list, callback):
        print(f"EVENT_SUBSCRIBED: {topics}")
    
    def close(self):
        pass
    
    async def _ensure_connected(self):
        return True

import json
import logging
import asyncio
import redis.asyncio as redis
from .interface import EventBusInterface

logger = logging.getLogger(__name__)

class RedisEventBus(EventBusInterface):
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None
        self._pubsub = None

    async def _ensure_connected(self):
        """Lazy initialization with retry logic for Render async startup."""
        if self.redis is not None:
            return True
        
        retries = 5
        backoff = 2
        for i in range(retries):
            try:
                self.redis = redis.from_url(self.redis_url)
                await self.redis.ping()
                logger.info(f"Successfully connected to Redis Event Bus (Attempt {i+1})")
                return True
            except Exception as e:
                logger.warning(f"Redis connection attempt {i+1} failed: {e}. Retrying in {backoff}s...")
                await asyncio.sleep(backoff)
                backoff *= 2
        
        logger.error("Could not connect to Redis after multiple attempts. Operating in disconnected mode.")
        return False

    async def emit(self, topic: str, message: dict):
        if not await self._ensure_connected():
            return
        try:
            await self.redis.publish(topic, json.dumps(message))
        except Exception as e:
            logger.error(f"Redis publish error: {e}")

    async def subscribe(self, topics: list, callback):
        if not await self._ensure_connected():
            return
        
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(*topics)
        try:
            async for message in self._pubsub.listen():
                if message['type'] == 'message':
                    topic = message['channel'].decode('utf-8')
                    payload = json.loads(message['data'].decode('utf-8'))
                    await callback(topic, payload)
        finally:
            if self._pubsub:
                await self._pubsub.unsubscribe(*topics)

    def close(self):
        # Async instances are usually closed via the app lifecycle
        pass

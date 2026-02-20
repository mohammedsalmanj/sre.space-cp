import os
from .interface import EventBusInterface

_instance = None

def get_event_bus() -> EventBusInterface:
    global _instance
    if _instance is not None:
        return _instance

    # Import config here to avoid circular dependencies if any
    from apps.control_plane.runtime_config import EVENT_BUS as BUS_TYPE
    
    if BUS_TYPE == "kafka":
        from .kafka_bus import KafkaEventBus
        bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        _instance = KafkaEventBus(bootstrap)
    else:
        from .redis_bus import RedisEventBus
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _instance = RedisEventBus(url)
        
    return _instance

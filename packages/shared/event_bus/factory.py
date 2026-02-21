import os
from .interface import EventBusInterface

_instance = None

def get_event_bus() -> EventBusInterface:
    global _instance
    if _instance is not None:
        return _instance

    from apps.control_plane.config import EVENT_BUS as BUS_TYPE, KAFKA_BOOTSTRAP_SERVERS, REDIS_URL
    
    if BUS_TYPE == "kafka":
        try:
            from .kafka_bus import KafkaEventBus
            _instance = KafkaEventBus(KAFKA_BOOTSTRAP_SERVERS)
        except:
            from .local_bus import LocalEventBus
            _instance = LocalEventBus()
    elif BUS_TYPE == "redis":
        try:
            from .redis_bus import RedisEventBus
            _instance = RedisEventBus(REDIS_URL)
        except:
            from .local_bus import LocalEventBus
            _instance = LocalEventBus()
    else:
        from .local_bus import LocalEventBus
        _instance = LocalEventBus()
        
    return _instance

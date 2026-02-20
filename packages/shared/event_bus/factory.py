import os
from .interface import EventBusInterface

_instance = None

def get_event_bus() -> EventBusInterface:
    global _instance
    if _instance is not None:
        return _instance

    from apps.control_plane.runtime_config import EVENT_BUS as BUS_TYPE
    
    # Block 3: Force Redis in Cloud if Kafka isn't explicitly required
    env = os.getenv("ENV", "local")
    if env == "cloud" and BUS_TYPE != "redis":
        BUS_TYPE = "redis"
    if BUS_TYPE == "kafka":
        try:
            from .kafka_bus import KafkaEventBus
            bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            _instance = KafkaEventBus(bootstrap)
        except:
            from .local_bus import LocalEventBus
            _instance = LocalEventBus()
    elif BUS_TYPE == "redis":
        try:
            from .redis_bus import RedisEventBus
            url = os.getenv("REDIS_URL", "redis://localhost:6379")
            _instance = RedisEventBus(url)
        except:
            from .local_bus import LocalEventBus
            _instance = LocalEventBus()
    else:
        from .local_bus import LocalEventBus
        _instance = LocalEventBus()
        
    return _instance

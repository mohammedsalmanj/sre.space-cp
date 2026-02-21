import os
from .interface import EventBusInterface

# Singleton instance to ensure a single connection per process
_instance = None

def get_event_bus() -> EventBusInterface:
    """
    Factory Pattern for Event Bus Orchestration.
    
    This factory dynamically selects the messaging backbone based on the
    environment configuration (EVENT_BUS). It supports high-performance Kafka
    for local/enterprise mode and managed Redis for cloud deployments.
    """
    global _instance
    if _instance is not None:
        return _instance

    # Imports are lazy-loaded to prevent circular dependencies in the monorepo
    from apps.control_plane.config import EVENT_BUS as BUS_TYPE, KAFKA_BOOTSTRAP_SERVERS, REDIS_URL
    
    if BUS_TYPE == "kafka":
        try:
            # Full scale enterprise messaging
            from .kafka_bus import KafkaEventBus
            _instance = KafkaEventBus(KAFKA_BOOTSTRAP_SERVERS)
        except:
            # Fallback for environments without Kafka (laptop mode)
            from .local_bus import LocalEventBus
            _instance = LocalEventBus()
    elif BUS_TYPE == "redis":
        try:
            # Cloud-optimized messaging (Render/Heroku/AWS)
            from .redis_bus import RedisEventBus
            _instance = RedisEventBus(REDIS_URL)
        except:
            from .local_bus import LocalEventBus
            _instance = LocalEventBus()
    else:
        # Default in-memory bus for local testing
        from .local_bus import LocalEventBus
        _instance = LocalEventBus()
        
    return _instance

from abc import ABC, abstractmethod

class EventBusInterface(ABC):
    @abstractmethod
    async def emit(self, topic: str, message: dict):
        """Publish a message to a specific topic."""
        pass

    @abstractmethod
    async def subscribe(self, topics: list, callback):
        """Listen for messages on specific topics."""
        pass

    @abstractmethod
    def close(self):
        """Cleanup resources."""
        pass

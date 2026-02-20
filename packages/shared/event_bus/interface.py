from abc import ABC, abstractmethod

class EventBusInterface(ABC):
    @abstractmethod
    async def emit(self, topic: str, message: dict):
        pass

    @abstractmethod
    async def subscribe(self, topics: list, callback):
        pass

    @abstractmethod
    def close(self):
        pass

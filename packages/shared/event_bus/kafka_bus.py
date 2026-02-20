import json
import logging
from confluent_kafka import Producer
from .interface import EventBusInterface

logger = logging.getLogger(__name__)

class KafkaEventBus(EventBusInterface):
    def __init__(self, bootstrap_servers: str):
        self.conf = {'bootstrap.servers': bootstrap_servers}
        self.producer = Producer(self.conf)

    async def emit(self, topic: str, message: dict):
        try:
            self.producer.produce(topic, json.dumps(message).encode('utf-8'))
            self.producer.poll(0) 
        except Exception as e:
            logger.error(f"Kafka produce error: {e}")

    async def subscribe(self, topics: list, callback):
        from confluent_kafka import Consumer
        conf = {
            'bootstrap.servers': self.conf['bootstrap.servers'],
            'group.id': 'sre-group',
            'auto.offset.reset': 'latest'
        }
        consumer = Consumer(conf)
        consumer.subscribe(topics)
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None: continue
                if msg.error(): continue
                await callback(msg.topic(), json.loads(msg.value().decode('utf-8')))
                await asyncio.sleep(0)
        finally:
            consumer.close()

    def close(self):
        self.producer.flush()

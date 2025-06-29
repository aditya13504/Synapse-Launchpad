import json
import os
from typing import Dict, Any
from kafka import KafkaProducer
import logging
import asyncio

logger = logging.getLogger(__name__)

class KafkaPublisher:
    """
    Kafka publisher for market pulse events
    """
    
    def __init__(self):
        self.kafka_servers = os.getenv("KAFKA_SERVERS", "localhost:9092").split(",")
        self.producer: KafkaProducer = None
    
    async def initialize(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                retry_backoff_ms=1000
            )
            
            logger.info("Kafka producer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            # Continue without Kafka if not available
            self.producer = None
    
    async def close(self):
        """Close Kafka producer"""
        try:
            if self.producer:
                self.producer.close()
            logger.info("Kafka producer closed")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")
    
    async def health_check(self) -> bool:
        """Check Kafka connection health"""
        try:
            if self.producer:
                # Try to get metadata to check connection
                metadata = self.producer.bootstrap_connected()
                return metadata
            return False
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return False
    
    async def publish_event(self, topic: str, event: Dict[str, Any], key: str = None):
        """Publish event to Kafka topic"""
        try:
            if not self.producer:
                logger.warning("Kafka producer not available, skipping event publication")
                return
            
            # Use company name as key for partitioning
            if not key and 'company' in event:
                key = event['company']
            
            # Send event
            future = self.producer.send(
                topic=topic,
                value=event,
                key=key
            )
            
            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Published event to {topic} (partition: {record_metadata.partition}, offset: {record_metadata.offset})")
            
        except Exception as e:
            logger.error(f"Failed to publish event to Kafka: {e}")
    
    async def publish_batch_events(self, topic: str, events: list):
        """Publish multiple events to Kafka topic"""
        try:
            if not self.producer:
                logger.warning("Kafka producer not available, skipping batch publication")
                return
            
            for event in events:
                key = event.get('company', event.get('event_id'))
                self.producer.send(
                    topic=topic,
                    value=event,
                    key=key
                )
            
            # Flush to ensure all messages are sent
            self.producer.flush()
            
            logger.info(f"Published {len(events)} events to {topic}")
            
        except Exception as e:
            logger.error(f"Failed to publish batch events to Kafka: {e}")
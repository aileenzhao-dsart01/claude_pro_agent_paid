"""Message queue implementation for agent communication."""

import json
import asyncio
import logging
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
import redis.asyncio as redis
from pydantic import BaseModel

from ..database.models import TaskStatus, AgentStatus


class Message(BaseModel):
    """Message format for agent communication."""
    id: str
    type: str
    sender: str
    recipient: Optional[str] = None  # None for broadcast
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    priority: int = 1  # 1=high, 2=medium, 3=low
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None


class MessageQueue:
    """Redis-based message queue for agent communication."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.logger = logging.getLogger("message_queue")
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.psubscribe: Optional[redis.client.PubSub] = None

    async def connect(self):
        """Connect to Redis."""
        self.redis = await redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        self.logger.info(f"Connected to Redis at {self.redis_url}")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.logger.info("Disconnected from Redis")

    async def publish(self, channel: str, message: Message) -> bool:
        """Publish a message to a channel."""
        if not self.redis:
            raise ConnectionError("Not connected to Redis")

        try:
            message_dict = message.dict()
            message_dict["timestamp"] = message_dict["timestamp"].isoformat()

            await self.redis.publish(
                channel,
                json.dumps(message_dict)
            )
            self.logger.debug(f"Published message {message.id} to channel {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish message: {str(e)}")
            return False

    async def subscribe(self, channel: str, callback: Callable[[Message], None]):
        """Subscribe to a channel."""
        if not self.redis:
            raise ConnectionError("Not connected to Redis")

        if channel not in self.subscriptions:
            self.subscriptions[channel] = []

        self.subscriptions[channel].append(callback)
        self.logger.info(f"Subscribed to channel {channel}")

    async def unsubscribe(self, channel: str, callback: Callable[[Message], None]):
        """Unsubscribe from a channel."""
        if channel in self.subscriptions:
            if callback in self.subscriptions[channel]:
                self.subscriptions[channel].remove(callback)
                self.logger.info(f"Unsubscribed from channel {channel}")

    async def start_listening(self):
        """Start listening for messages on subscribed channels."""
        if not self.redis:
            raise ConnectionError("Not connected to Redis")

        self.psubscribe = self.redis.pubsub()

        # Subscribe to all channels we have callbacks for
        channels = list(self.subscriptions.keys())
        if channels:
            await self.psubscribe.subscribe(*channels)

        async for message in self.psubscribe.listen():
            if message["type"] == "message":
                channel = message["channel"]
                data = json.loads(message["data"])

                # Convert timestamp string back to datetime
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])

                msg = Message(**data)

                # Call all callbacks for this channel
                if channel in self.subscriptions:
                    for callback in self.subscriptions[channel]:
                        try:
                            await callback(msg)
                        except Exception as e:
                            self.logger.error(f"Error in callback for channel {channel}: {str(e)}")

    async def stop_listening(self):
        """Stop listening for messages."""
        if self.psubscribe:
            await self.psubscribe.unsubscribe()
            await self.psubscribe.close()
            self.logger.info("Stopped listening for messages")

    async def send_task(self, task_type: str, payload: Dict[str, Any],
                       priority: int = 2, recipient: Optional[str] = None) -> str:
        """Send a task message."""
        message = Message(
            id=f"msg_{datetime.utcnow().timestamp()}",
            type="task",
            sender="system",
            recipient=recipient,
            payload={
                "task_type": task_type,
                "task_data": payload,
                "priority": priority
            },
            priority=priority
        )

        channel = f"tasks:{task_type}" if not recipient else f"agent:{recipient}"
        await self.publish(channel, message)
        return message.id

    async def send_response(self, original_message: Message,
                           response_payload: Dict[str, Any]) -> str:
        """Send a response to a message."""
        message = Message(
            id=f"msg_{datetime.utcnow().timestamp()}",
            type="response",
            sender="system",
            recipient=original_message.sender,
            payload=response_payload,
            correlation_id=original_message.id
        )

        channel = f"agent:{original_message.sender}"
        await self.publish(channel, message)
        return message.id

    async def broadcast_system_status(self, status: Dict[str, Any]):
        """Broadcast system status to all agents."""
        message = Message(
            id=f"status_{datetime.utcnow().timestamp()}",
            type="system_status",
            sender="supervisor",
            payload=status
        )

        await self.publish("system:status", message)

    async def queue_task(self, queue_name: str, task: Dict[str, Any],
                        priority: int = 2) -> str:
        """Queue a task in a Redis list for delayed processing."""
        if not self.redis:
            raise ConnectionError("Not connected to Redis")

        task_id = f"task_{datetime.utcnow().timestamp()}"
        task_data = {
            "id": task_id,
            "data": task,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat()
        }

        # Use sorted set for priority queueing
        await self.redis.zadd(
            f"queue:{queue_name}",
            {json.dumps(task_data): priority}
        )

        self.logger.info(f"Queued task {task_id} in {queue_name} with priority {priority}")
        return task_id

    async def dequeue_task(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Dequeue the highest priority task from a queue."""
        if not self.redis:
            raise ConnectionError("Not connected to Redis")

        # Get and remove the highest priority task
        result = await self.redis.zpopmin(f"queue:{queue_name}")

        if result:
            task_data = json.loads(result[0][0])
            task_data["data"]["dequeued_at"] = datetime.utcnow().isoformat()
            return task_data

        return None

    async def get_queue_length(self, queue_name: str) -> int:
        """Get the length of a queue."""
        if not self.redis:
            raise ConnectionError("Not connected to Redis")

        return await self.redis.zcard(f"queue:{queue_name}")
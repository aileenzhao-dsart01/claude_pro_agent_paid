"""Base agent class for all marketing agents."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Status of an agent."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Task model for agent tasks."""
    id: str
    type: str
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        use_enum_values = True


class BaseAgent(ABC):
    """Base class for all marketing agents."""

    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agent.{agent_id}")

    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task and return results."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent has."""
        pass

    def validate_task(self, task: Task) -> bool:
        """Validate if this agent can handle the task."""
        return task.type in self.get_capabilities()

    async def execute(self, task: Task) -> Task:
        """Execute a task with proper error handling."""
        self.status = AgentStatus.PROCESSING
        task.status = AgentStatus.PROCESSING
        task.assigned_to = self.agent_id

        try:
            self.logger.info(f"Starting task {task.id} of type {task.type}")
            result = await self.process_task(task)
            task.result = result
            task.status = AgentStatus.COMPLETED
            self.logger.info(f"Completed task {task.id}")
        except Exception as e:
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            task.status = AgentStatus.ERROR
            task.error = str(e)
        finally:
            self.status = AgentStatus.IDLE

        return task

    def __str__(self) -> str:
        return f"{self.name} ({self.agent_id})"
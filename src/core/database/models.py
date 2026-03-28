"""Database models for marketing agent system."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .session import Base


class AgentStatus(str, enum.Enum):
    """Status of an agent."""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"


class TaskPriority(str, enum.Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    """Status of a task."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CampaignStatus(str, enum.Enum):
    """Status of a marketing campaign."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Agent(Base):
    """Agent model representing a marketing agent."""

    __tablename__ = "agents"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    agent_type = Column(String(50), nullable=False)  # research, execution, analytics, etc.
    capabilities = Column(JSON, default=list)  # List of task types this agent can handle
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)
    config = Column(JSON, default=dict)  # Agent-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_heartbeat = Column(DateTime)

    # Relationships
    tasks = relationship("Task", back_populates="agent")
    performance_metrics = relationship("AgentPerformance", back_populates="agent")


class Task(Base):
    """Task model representing work to be done by agents."""

    __tablename__ = "tasks"

    id = Column(String(50), primary_key=True)
    type = Column(String(50), nullable=False)  # keyword_research, ad_creation, etc.
    payload = Column(JSON, default=dict)  # Task data
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    assigned_to = Column(String(50), ForeignKey("agents.id"))
    result = Column(JSON)  # Task result data
    error = Column(Text)  # Error message if task failed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    timeout_seconds = Column(Integer, default=300)  # Default 5 minutes
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    workflow_tasks = relationship("WorkflowTask", back_populates="task")
    campaign_tasks = relationship("CampaignTask", back_populates="task")


class Workflow(Base):
    """Workflow model for multi-step processes."""

    __tablename__ = "workflows"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    steps = Column(JSON)  # List of step definitions
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_by = Column(String(100))  # User or system that created the workflow

    # Relationships
    workflow_tasks = relationship("WorkflowTask", back_populates="workflow")


class WorkflowTask(Base):
    """Association between workflows and tasks."""

    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(50), ForeignKey("workflows.id"))
    task_id = Column(String(50), ForeignKey("tasks.id"))
    step_number = Column(Integer, nullable=False)
    depends_on = Column(JSON)  # List of step numbers this step depends on
    condition = Column(JSON)  # Conditional logic for step execution

    # Relationships
    workflow = relationship("Workflow", back_populates="workflow_tasks")
    task = relationship("Task", back_populates="workflow_tasks")


class Campaign(Base):
    """Marketing campaign model."""

    __tablename__ = "campaigns"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    platform = Column(String(50))  # google_ads, facebook_ads, etc.
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    budget = Column(Integer)  in cents
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    target_audience = Column(JSON)
    keywords = Column(JSON)
    ad_groups = Column(JSON)
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    campaign_tasks = relationship("CampaignTask", back_populates="campaign")


class CampaignTask(Base):
    """Association between campaigns and tasks."""

    __tablename__ = "campaign_tasks"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(String(50), ForeignKey("campaigns.id"))
    task_id = Column(String(50), ForeignKey("tasks.id"))
    task_type = Column(String(50))  # campaign_setup, ad_creation, etc.
    stage = Column(String(50))  # planning, execution, optimization

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_tasks")
    task = relationship("Task", back_populates="campaign_tasks")


class AgentPerformance(Base):
    """Performance metrics for agents."""

    __tablename__ = "agent_performance"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(50), ForeignKey("agents.id"))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    avg_processing_time = Column(Integer)  in seconds
    success_rate = Column(Integer)  # percentage
    cost_usage = Column(Integer)  in cents
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    agent = relationship("Agent", back_populates="performance_metrics")


class SystemLog(Base):
    """System log for auditing and debugging."""

    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    component = Column(String(50), nullable=False)  # supervisor, research_agent, etc.
    message = Column(Text, nullable=False)
    details = Column(JSON)
    trace_id = Column(String(100))  # For correlating related logs
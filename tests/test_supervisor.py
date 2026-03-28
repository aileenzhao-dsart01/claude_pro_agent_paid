"""Tests for supervisor agent."""

import asyncio
import pytest
from datetime import datetime

from src.agents.supervisor import Supervisor
from src.agents.research_agent import ResearchAgent
from src.agents.base import Task, TaskPriority, AgentStatus


@pytest.fixture
def supervisor():
    """Create supervisor fixture."""
    return Supervisor()


@pytest.fixture
def research_agent():
    """Create research agent fixture."""
    return ResearchAgent()


@pytest.mark.asyncio
async def test_supervisor_initialization(supervisor):
    """Test supervisor initialization."""
    assert supervisor.agent_id == "supervisor_001"
    assert supervisor.name == "Marketing Team Supervisor"
    assert supervisor.status == AgentStatus.IDLE
    assert "coordination" in supervisor.get_capabilities()


@pytest.mark.asyncio
async def test_register_agent(supervisor, research_agent):
    """Test agent registration."""
    result = await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    assert result["status"] == "registered"
    assert result["agent_id"] == research_agent.agent_id
    assert result["total_agents"] == 1
    assert research_agent.agent_id in supervisor.agents
    assert supervisor.agent_status[research_agent.agent_id] == AgentStatus.IDLE


@pytest.mark.asyncio
async def test_system_status(supervisor, research_agent):
    """Test system status retrieval."""
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    status = await supervisor._get_system_status()

    assert status["total_agents"] == 1
    assert status["idle_agents"] == 1
    assert status["busy_agents"] == 0
    assert status["queued_tasks"] == 0
    assert status["completed_tasks"] == 0
    assert research_agent.agent_id in status["agent_status"]
    assert status["agent_status"][research_agent.agent_id] == "idle"


@pytest.mark.asyncio
async def test_task_assignment(supervisor, research_agent):
    """Test task assignment to agent."""
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    task_result = await supervisor._assign_task({
        "task_type": "keyword_research",
        "task_data": {
            "keywords": ["test keyword"],
            "location": "US"
        },
        "priority": "high"
    })

    assert "task_id" in task_result
    assert task_result["status"] in ["assigned", "queued"]

    if task_result["status"] == "assigned":
        assert task_result["agent_id"] == research_agent.agent_id

        # Wait for task completion
        await asyncio.sleep(0.5)

        task = supervisor.get_task_status(task_result["task_id"])
        assert task is not None
        assert task.status in [AgentStatus.COMPLETED, AgentStatus.PROCESSING]


@pytest.mark.asyncio
async def test_task_queuing(supervisor, research_agent):
    """Test task queuing when agent is busy."""
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    # Mark agent as busy
    supervisor.agent_status[research_agent.agent_id] = AgentStatus.PROCESSING

    task_result = await supervisor._assign_task({
        "task_type": "keyword_research",
        "task_data": {"keywords": ["test"]},
        "priority": "medium"
    })

    assert task_result["status"] == "queued"
    assert task_result["queue_position"] > 0
    assert len(supervisor.task_queue) == 1


@pytest.mark.asyncio
async def test_task_history(supervisor, research_agent):
    """Test task history tracking."""
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    task_result = await supervisor._assign_task({
        "task_type": "keyword_research",
        "task_data": {"keywords": ["history test"]},
        "priority": "low"
    })

    task_id = task_result["task_id"]
    await asyncio.sleep(0.5)

    task = supervisor.get_task_status(task_id)
    assert task is not None
    assert task.id == task_id
    assert task.type == "keyword_research"


@pytest.mark.asyncio
async def test_agent_performance(supervisor, research_agent):
    """Test agent performance metrics."""
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    # Assign and complete a task
    task_result = await supervisor._assign_task({
        "task_type": "keyword_research",
        "task_data": {"keywords": ["performance test"]},
        "priority": "medium"
    })

    await asyncio.sleep(0.5)

    performance = supervisor.get_agent_performance(research_agent.agent_id)

    assert performance["agent_id"] == research_agent.agent_id
    assert performance["total_tasks"] >= 1
    assert performance["success_rate"] >= 0


@pytest.mark.asyncio
async def test_workflow_creation(supervisor, research_agent):
    """Test workflow creation."""
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })

    workflow_result = await supervisor._create_workflow({
        "steps": [
            {
                "type": "keyword_research",
                "payload": {"keywords": ["workflow test"]},
                "priority": "high"
            }
        ]
    })

    assert "workflow_id" in workflow_result
    assert workflow_result["total_steps"] == 1
    assert workflow_result["status"] == "started"
    assert workflow_result["first_task_id"] is not None


@pytest.mark.asyncio
async def test_invalid_task_type(supervisor):
    """Test handling of invalid task type."""
    with pytest.raises(ValueError, match="No agents capable"):
        await supervisor._assign_task({
            "task_type": "invalid_task_type",
            "task_data": {},
            "priority": "high"
        })


def test_task_model():
    """Test task model creation."""
    task = Task(
        id="test_task_1",
        type="test_type",
        payload={"key": "value"},
        priority=TaskPriority.HIGH
    )

    assert task.id == "test_task_1"
    assert task.type == "test_type"
    assert task.payload == {"key": "value"}
    assert task.priority == TaskPriority.HIGH
    assert task.status == AgentStatus.IDLE
    assert task.created_at is not None
"""Supervisor agent for coordinating marketing agent team."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque

from .base import BaseAgent, Task, TaskPriority, AgentStatus


class Supervisor(BaseAgent):
    """Supervisor agent coordinates tasks across all agents."""

    def __init__(self):
        super().__init__(
            agent_id="supervisor_001",
            name="Marketing Team Supervisor",
            description="Coordinates tasks across all marketing agents and manages workflows"
        )
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = deque()
        self.task_history: Dict[str, Task] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        self.logger = logging.getLogger("supervisor")

    def get_capabilities(self) -> List[str]:
        """Return capabilities of supervisor."""
        return ["coordination", "task_assignment", "workflow_management", "monitoring"]

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a coordination task."""
        if task.type == "assign_task":
            return await self._assign_task(task.payload)
        elif task.type == "register_agent":
            return await self._register_agent(task.payload)
        elif task.type == "get_system_status":
            return await self._get_system_status()
        elif task.type == "create_workflow":
            return await self._create_workflow(task.payload)
        else:
            raise ValueError(f"Unknown task type: {task.type}")

    async def _assign_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a task to the appropriate agent."""
        task_type = payload.get("task_type")
        task_data = payload.get("task_data", {})
        priority = payload.get("priority", "medium")

        # Find capable agents
        capable_agents = [
            agent_id for agent_id, agent in self.agents.items()
            if task_type in agent.get_capabilities()
        ]

        if not capable_agents:
            raise ValueError(f"No agents capable of handling task type: {task_type}")

        # Find available agent
        available_agents = [
            agent_id for agent_id in capable_agents
            if self.agent_status.get(agent_id) == AgentStatus.IDLE
        ]

        if not available_agents:
            # All capable agents are busy, queue the task
            task = Task(
                id=f"task_{len(self.task_history) + 1}",
                type=task_type,
                payload=task_data,
                priority=TaskPriority(priority)
            )
            self.task_queue.append(task)
            self.task_history[task.id] = task

            return {
                "status": "queued",
                "task_id": task.id,
                "message": f"Task queued. {len(capable_agents)} capable agents are busy.",
                "queue_position": len(self.task_queue)
            }

        # Assign to first available agent
        agent_id = available_agents[0]
        agent = self.agents[agent_id]

        task = Task(
            id=f"task_{len(self.task_history) + 1}",
            type=task_type,
            payload=task_data,
            priority=TaskPriority(priority)
        )

        self.task_history[task.id] = task
        self.agent_status[agent_id] = AgentStatus.PROCESSING

        # Execute task asynchronously
        asyncio.create_task(self._execute_agent_task(agent, task))

        return {
            "status": "assigned",
            "task_id": task.id,
            "agent_id": agent_id,
            "agent_name": agent.name
        }

    async def _execute_agent_task(self, agent: BaseAgent, task: Task):
        """Execute task with agent and update status."""
        try:
            result = await agent.execute(task)
            self.task_history[task.id] = result
            self.agent_status[agent.agent_id] = AgentStatus.IDLE

            # Check for queued tasks that this agent can handle
            await self._process_queue()
        except Exception as e:
            self.logger.error(f"Error in agent task execution: {str(e)}")
            task.status = AgentStatus.ERROR
            task.error = str(e)
            self.task_history[task.id] = task
            self.agent_status[agent.agent_id] = AgentStatus.IDLE

    async def _register_agent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new agent with the supervisor."""
        agent_id = payload.get("agent_id")
        agent = payload.get("agent")

        if not agent_id or not agent:
            raise ValueError("Both agent_id and agent are required")

        if agent_id in self.agents:
            raise ValueError(f"Agent with id {agent_id} already registered")

        # In a real implementation, agent would be a BaseAgent instance
        # For now, we'll store metadata
        self.agents[agent_id] = agent
        self.agent_status[agent_id] = AgentStatus.IDLE

        self.logger.info(f"Registered agent: {agent_id}")
        return {
            "status": "registered",
            "agent_id": agent_id,
            "total_agents": len(self.agents)
        }

    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        idle_agents = sum(
            1 for status in self.agent_status.values()
            if status == AgentStatus.IDLE
        )
        busy_agents = len(self.agents) - idle_agents

        return {
            "total_agents": len(self.agents),
            "idle_agents": idle_agents,
            "busy_agents": busy_agents,
            "queued_tasks": len(self.task_queue),
            "completed_tasks": sum(
                1 for task in self.task_history.values()
                if task.status == AgentStatus.COMPLETED
            ),
            "failed_tasks": sum(
                1 for task in self.task_history.values()
                if task.status == AgentStatus.ERROR
            ),
            "agent_status": {
                agent_id: status.value for agent_id, status in self.agent_status.items()
            }
        }

    async def _create_workflow(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a multi-step workflow."""
        steps = payload.get("steps", [])
        workflow_id = f"workflow_{len(self.task_history) + 1}"

        if not steps:
            raise ValueError("Workflow must have at least one step")

        workflow_tasks = []
        for i, step in enumerate(steps):
            task = Task(
                id=f"{workflow_id}_step_{i + 1}",
                type=step.get("type"),
                payload=step.get("payload", {}),
                priority=TaskPriority(step.get("priority", "medium"))
            )
            workflow_tasks.append(task)

        # Store workflow definition
        self.task_history[workflow_id] = Task(
            id=workflow_id,
            type="workflow",
            payload={"steps": [t.dict() for t in workflow_tasks]},
            status=AgentStatus.IDLE
        )

        # Execute first step
        if workflow_tasks:
            first_task = workflow_tasks[0]
            await self._assign_task({
                "task_type": first_task.type,
                "task_data": first_task.payload,
                "priority": first_task.priority.value
            })

        return {
            "workflow_id": workflow_id,
            "total_steps": len(workflow_tasks),
            "status": "started",
            "first_task_id": workflow_tasks[0].id if workflow_tasks else None
        }

    async def _process_queue(self):
        """Process tasks in the queue when agents become available."""
        if not self.task_queue:
            return

        # Try to assign queued tasks to available agents
        tasks_to_remove = []
        for task in list(self.task_queue):
            capable_agents = [
                agent_id for agent_id, agent in self.agents.items()
                if task.type in agent.get_capabilities()
                and self.agent_status.get(agent_id) == AgentStatus.IDLE
            ]

            if capable_agents:
                agent_id = capable_agents[0]
                agent = self.agents[agent_id]

                self.agent_status[agent_id] = AgentStatus.PROCESSING
                tasks_to_remove.append(task)

                asyncio.create_task(self._execute_agent_task(agent, task))

        # Remove assigned tasks from queue
        for task in tasks_to_remove:
            self.task_queue.remove(task)

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get status of a specific task."""
        return self.task_history.get(task_id)

    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for an agent."""
        agent_tasks = [
            task for task in self.task_history.values()
            if task.assigned_to == agent_id
        ]

        completed = sum(1 for t in agent_tasks if t.status == AgentStatus.COMPLETED)
        failed = sum(1 for t in agent_tasks if t.status == AgentStatus.ERROR)
        total = len(agent_tasks)

        return {
            "agent_id": agent_id,
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "success_rate": completed / total if total > 0 else 0,
            "recent_tasks": [t.dict() for t in agent_tasks[-5:]] if agent_tasks else []
        }
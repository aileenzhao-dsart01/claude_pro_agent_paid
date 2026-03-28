"""FastAPI application for marketing agent dashboard."""

import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager

from ...agents.supervisor import Supervisor
from ...core.config import settings
from ...core.database.models import Base
from ...core.database.session import SessionLocal, engine
from ...core.messaging.queue import MessageQueue

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("dashboard")

# Create database tables
Base.metadata.create_all(bind=engine)

# API key security
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key."""
    if not settings.API_KEYS:
        return True  # No API keys required

    if api_key not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True


# Global supervisor instance
supervisor: Supervisor = None
message_queue: MessageQueue = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    # Startup
    global supervisor, message_queue

    logger.info("Starting marketing agent system...")

    # Initialize supervisor
    supervisor = Supervisor()
    logger.info(f"Supervisor initialized: {supervisor.name}")

    # Initialize message queue
    message_queue = MessageQueue(redis_url=settings.REDIS_URL)
    await message_queue.connect()
    logger.info("Message queue initialized")

    yield

    # Shutdown
    logger.info("Shutting down marketing agent system...")

    if message_queue:
        await message_queue.disconnect()
        logger.info("Message queue disconnected")

    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Marketing Agent Team System",
    description="Automated paid advertising marketing agent team",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "name": "Marketing Agent Team System",
        "version": "1.0.0",
        "status": "operational",
        "description": "Automated paid advertising marketing agent team"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "supervisor": "active" if supervisor else "inactive"
    }


@app.get("/api/system/status", dependencies=[Depends(get_api_key)])
async def get_system_status():
    """Get current system status."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    try:
        task = {
            "id": "status_check",
            "type": "get_system_status",
            "payload": {}
        }
        result = await supervisor.process_task(task)
        return result
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks", dependencies=[Depends(get_api_key)])
async def create_task(task_request: Dict[str, Any]):
    """Create a new task."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    required_fields = ["type", "data"]
    for field in required_fields:
        if field not in task_request:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    try:
        task = {
            "id": f"api_task_{len(supervisor.task_history) + 1}",
            "type": "assign_task",
            "payload": {
                "task_type": task_request["type"],
                "task_data": task_request["data"],
                "priority": task_request.get("priority", "medium")
            }
        }
        result = await supervisor.process_task(task)
        return result
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", dependencies=[Depends(get_api_key)])
async def get_task_status(task_id: str):
    """Get status of a specific task."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    task = supervisor.get_task_status(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {
        "id": task.id,
        "type": task.type,
        "status": task.status.value,
        "assigned_to": task.assigned_to,
        "priority": task.priority.value,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "result": task.result,
        "error": task.error
    }


@app.post("/api/agents/register", dependencies=[Depends(get_api_key)])
async def register_agent(agent_data: Dict[str, Any]):
    """Register a new agent with the supervisor."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    required_fields = ["agent_id", "name", "description", "capabilities"]
    for field in required_fields:
        if field not in agent_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    try:
        # Create a simple agent object for registration
        # In a real implementation, this would be an actual agent instance
        agent_info = {
            "agent_id": agent_data["agent_id"],
            "agent": {
                "agent_id": agent_data["agent_id"],
                "name": agent_data["name"],
                "description": agent_data["description"],
                "get_capabilities": lambda: agent_data["capabilities"]
            }
        }

        task = {
            "id": f"register_agent_{agent_data['agent_id']}",
            "type": "register_agent",
            "payload": agent_info
        }

        result = await supervisor.process_task(task)
        return result
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents", dependencies=[Depends(get_api_key)])
async def list_agents():
    """List all registered agents."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    agents = []
    for agent_id, agent in supervisor.agents.items():
        agents.append({
            "id": agent_id,
            "name": agent.name if hasattr(agent, "name") else agent_id,
            "description": agent.description if hasattr(agent, "description") else "",
            "status": supervisor.agent_status.get(agent_id, "unknown").value,
            "capabilities": agent.get_capabilities() if hasattr(agent, "get_capabilities") else []
        })

    return {"agents": agents}


@app.get("/api/agents/{agent_id}/performance", dependencies=[Depends(get_api_key)])
async def get_agent_performance(agent_id: str):
    """Get performance metrics for an agent."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    if agent_id not in supervisor.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    performance = supervisor.get_agent_performance(agent_id)
    return performance


@app.post("/api/workflows", dependencies=[Depends(get_api_key)])
async def create_workflow(workflow_data: Dict[str, Any]):
    """Create a new workflow."""
    if not supervisor:
        raise HTTPException(status_code=503, detail="Supervisor not initialized")

    required_fields = ["name", "steps"]
    for field in required_fields:
        if field not in workflow_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )

    try:
        task = {
            "id": f"workflow_{len(supervisor.task_history) + 1}",
            "type": "create_workflow",
            "payload": {
                "steps": workflow_data["steps"],
                "name": workflow_data["name"],
                "description": workflow_data.get("description", "")
            }
        }
        result = await supervisor.process_task(task)
        return result
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/message-queue/stats", dependencies=[Depends(get_api_key)])
async def get_queue_stats():
    """Get message queue statistics."""
    if not message_queue:
        raise HTTPException(status_code=503, detail="Message queue not initialized")

    try:
        # Get queue lengths for common queues
        queues = ["tasks:research", "tasks:execution", "tasks:analytics", "tasks:content"]
        stats = {}

        for queue in queues:
            length = await message_queue.get_queue_length(queue)
            stats[queue] = length

        return {
            "queues": stats,
            "total_messages": sum(stats.values())
        }
    except Exception as e:
        logger.error(f"Error getting queue stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
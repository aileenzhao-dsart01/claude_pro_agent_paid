#!/usr/bin/env python3
"""Main entry point for the marketing agent system."""

import asyncio
import logging
from datetime import datetime

from src.agents.supervisor import Supervisor
from src.agents.research_agent import ResearchAgent


async def demonstrate_supervisor():
    """Demonstrate the supervisor agent functionality."""
    print("=== Marketing Agent System Demo ===\n")

    # Initialize supervisor
    supervisor = Supervisor()
    print(f"1. Initialized Supervisor: {supervisor.name}")

    # Initialize research agent
    research_agent = ResearchAgent()
    print(f"2. Initialized Research Agent: {research_agent.name}")

    # Register research agent with supervisor
    await supervisor._register_agent({
        "agent_id": research_agent.agent_id,
        "agent": research_agent
    })
    print(f"3. Registered {research_agent.name} with supervisor")

    # Get system status
    status = await supervisor._get_system_status()
    print(f"4. System Status: {status['total_agents']} agent(s), {status['idle_agents']} idle")

    # Create a keyword research task
    print("\n5. Creating keyword research task...")
    task_result = await supervisor._assign_task({
        "task_type": "keyword_research",
        "task_data": {
            "keywords": ["digital marketing", "seo services", "social media marketing"],
            "location": "US",
            "language": "en"
        },
        "priority": "high"
    })

    print(f"   Task assigned: {task_result}")
    task_id = task_result.get("task_id")

    # Wait for task completion
    print("\n6. Waiting for task completion...")
    await asyncio.sleep(2)  # Simulate processing time

    # Check task status
    task = supervisor.get_task_status(task_id)
    if task:
        print(f"   Task Status: {task.status.value}")
        if task.result:
            print(f"   Task completed with {len(task.result.get('results', []))} keyword results")
            print(f"   First result: {task.result['results'][0]['keyword']} - "
                  f"Volume: {task.result['results'][0]['search_volume']}, "
                  f"CPC: ${task.result['results'][0]['cpc']:.2f}")

    # Create a competition analysis task
    print("\n7. Creating competition analysis task...")
    task_result2 = await supervisor._assign_task({
        "task_type": "competition_analysis",
        "task_data": {
            "keywords": ["email marketing software", "crm tools"],
            "depth": "moderate"
        },
        "priority": "medium"
    })

    print(f"   Task assigned: {task_result2}")
    task_id2 = task_result2.get("task_id")

    # Wait for second task completion
    await asyncio.sleep(2)

    # Check second task status
    task2 = supervisor.get_task_status(task_id2)
    if task2:
        print(f"   Task Status: {task2.status.value}")
        if task2.result:
            print(f"   Competition analysis completed for {len(task2.result['results'])} keywords")

    # Get agent performance
    print("\n8. Agent Performance:")
    performance = supervisor.get_agent_performance(research_agent.agent_id)
    print(f"   Tasks Completed: {performance['completed_tasks']}")
    print(f"   Tasks Failed: {performance['failed_tasks']}")
    print(f"   Success Rate: {performance['success_rate']:.1%}")

    # Create a workflow
    print("\n9. Creating multi-step workflow...")
    workflow_result = await supervisor._create_workflow({
        "steps": [
            {
                "type": "keyword_research",
                "payload": {
                    "keywords": ["content marketing"],
                    "location": "US"
                },
                "priority": "high"
            },
            {
                "type": "competition_analysis",
                "payload": {
                    "keywords": ["content marketing"],
                    "depth": "detailed"
                },
                "priority": "medium"
            },
            {
                "type": "market_trends",
                "payload": {
                    "keywords": ["content marketing"],
                    "time_range": "past_90_days"
                },
                "priority": "medium"
            }
        ]
    })

    print(f"   Workflow created: {workflow_result['workflow_id']}")
    print(f"   Total steps: {workflow_result['total_steps']}")
    print(f"   First task ID: {workflow_result['first_task_id']}")

    # Final system status
    print("\n10. Final System Status:")
    final_status = await supervisor._get_system_status()
    print(f"    Total Agents: {final_status['total_agents']}")
    print(f"    Busy Agents: {final_status['busy_agents']}")
    print(f"    Queued Tasks: {final_status['queued_tasks']}")
    print(f"    Completed Tasks: {final_status['completed_tasks']}")
    print(f"    Failed Tasks: {final_status['failed_tasks']}")

    print("\n=== Demo Complete ===")


async def run_web_server():
    """Run the FastAPI web server."""
    import uvicorn
    from src.core.config import settings

    print(f"\nStarting web server on http://{settings.APP_HOST}:{settings.APP_PORT}")
    config = uvicorn.Config(
        "src.web.dashboard.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """Main function."""
    print("Marketing Agent Team System")
    print("==========================")
    print("1. Run supervisor demo")
    print("2. Start web server")
    print("3. Exit")

    try:
        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            await demonstrate_supervisor()
        elif choice == "2":
            await run_web_server()
        elif choice == "3":
            print("Exiting...")
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\nInterrupted by user")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run main function
    asyncio.run(main())
# Marketing Agent Team System

A comprehensive paid advertising marketing agent team with multiple specialized roles for research, execution, analytics, testing, content creation, reporting, and supervision.

## Overview

This system automates and optimizes paid advertising campaigns across multiple platforms using a team of specialized AI agents. The system coordinates research, execution, analytics, and optimization tasks through a supervisor agent that manages workflow and communication.

## Features

- **Multi-Agent Architecture**: Supervisor coordinates specialized agents (research, execution, analytics, content, etc.)
- **Task Management**: Priority-based task queue with agent assignment and monitoring
- **Workflow Orchestration**: Multi-step campaign workflows with dependency management
- **Platform Integrations**: Google Ads API integration with support for additional platforms
- **Real-time Monitoring**: Web dashboard for system status and performance metrics
- **Message Queue**: Redis-based communication between agents
- **Database Persistence**: PostgreSQL for storing agents, tasks, campaigns, and performance data

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd marketing-agent-system
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up database and run migrations:
   ```bash
   alembic upgrade head
   ```

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- Application on port 8000
- pgAdmin on port 5050 (optional)

## Project Structure

```
marketing-agent-system/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── base.py         # Base agent class
│   │   ├── supervisor.py   # Supervisor agent
│   │   └── research_agent.py # Research agent
│   ├── core/               # Core infrastructure
│   │   ├── config.py       # Configuration management
│   │   ├── database/       # Database models and session
│   │   └── messaging/      # Message queue implementation
│   ├── integrations/       # Platform integrations
│   │   └── google_ads/     # Google Ads API client
│   └── web/
│       └── dashboard/      # FastAPI web application
├── tests/                  # Test suite
├── alembic/               # Database migrations
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker container definition
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── main.py               # Main entry point
```

## Usage

### Running the System

1. Start the web server:
   ```bash
   python main.py
   # Select option 2 to start web server
   ```

2. Access the dashboard:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### API Endpoints

- `GET /` - System information
- `GET /health` - Health check
- `GET /api/system/status` - System status
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{task_id}` - Get task status
- `POST /api/agents/register` - Register new agent
- `GET /api/agents` - List registered agents
- `POST /api/workflows` - Create multi-step workflow

### Creating a Research Task

```python
import requests

task = {
    "type": "keyword_research",
    "data": {
        "keywords": ["digital marketing", "seo services"],
        "location": "US",
        "language": "en"
    },
    "priority": "high"
}

response = requests.post(
    "http://localhost:8000/api/tasks",
    json=task,
    headers={"X-API-Key": "your-api-key"}
)
```

### Running the Demo

```bash
python main.py
# Select option 1 to run supervisor demo
```

## Agent Types

1. **Supervisor**: Coordinates all agents and manages workflows
2. **Research Agent**: Keyword research, competition analysis, market trends
3. **Execution Specialist**: Campaign creation and management (Google Ads, Facebook Ads)
4. **Digital Analyst**: Performance analytics and optimization recommendations
5. **Test Experiment Agent**: A/B testing and experiment management
6. **Content Creator**: Ad copy and creative generation
7. **Reporter**: Campaign reporting and insights

## Development

### Adding a New Agent

1. Create a new agent class in `src/agents/`:
   ```python
   from .base import BaseAgent

   class NewAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               agent_id="new_001",
               name="New Agent",
               description="Agent description"
           )

       def get_capabilities(self):
           return ["capability1", "capability2"]

       async def process_task(self, task):
           # Implement task processing
           pass
   ```

2. Register the agent with the supervisor via API or in initialization.

### Running Tests

```bash
pytest tests/
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Configuration

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marketing_agents
REDIS_URL=redis://localhost:6379/0

# LLM Providers
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=your-key

# Google Ads API
GOOGLE_ADS_CLIENT_ID=your-client-id
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token
```

## License

This project is available for experimentation and development. For production use, ensure compliance with platform API terms and data privacy regulations.

## Contributing

Contributions are welcome! Please create a feature branch and submit a pull request with clear description of changes.

---

*Built with Claude Code and AI-assisted development*# claude_pro_agent_paid

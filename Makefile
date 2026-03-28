# Marketing Agent Team System Makefile

.PHONY: help install dev test clean db-init db-migrate db-upgrade docker-up docker-down

help:
	@echo "Marketing Agent Team System"
	@echo "=========================="
	@echo "install     - Install dependencies"
	@echo "dev         - Run development server"
	@echo "test        - Run tests"
	@echo "clean       - Clean up temporary files"
	@echo "db-init     - Initialize database"
	@echo "db-migrate  - Create new migration"
	@echo "db-upgrade  - Apply migrations"
	@echo "docker-up   - Start services with Docker Compose"
	@echo "docker-down - Stop services"

install:
	pip install -r requirements.txt

dev:
	python main.py

test:
	pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true

db-init:
	python scripts/init_db.py

db-migrate:
	alembic revision --autogenerate -m "$(message)"

db-upgrade:
	alembic upgrade head

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-clean:
	docker-compose down -v
.PHONY: help install run test docker-build docker-run docker-stop clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run the FastAPI server locally"
	@echo "  test         - Run basic endpoint tests"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  clean        - Clean up Docker resources"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Testing basic endpoints..."
	@curl -s http://localhost:8000/ || echo "Server not running"
	@curl -s http://localhost:8000/health || echo "Health check failed"

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d
	@echo "API running at http://localhost:8000"
	@echo "Docs available at http://localhost:8000/docs"

docker-stop:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f
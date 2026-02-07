.PHONY: help setup up down restart logs build clean test dev-backend dev-frontend dev-up dev-down dev-backend-up dev-backend-down dev-frontend-up dev-frontend-down dev-status db-up db-down

# Load environment variables
include .env
export

# Default target
help:
	@echo "Simandaya Web - Available Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup & Development:"
	@echo "  make setup          - Initial setup (copy .env, create directories)"
	@echo "  make up             - Start all services (docker-compose up -d)"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make build          - Build all Docker images"
	@echo "  make rebuild        - Rebuild all images and restart"
	@echo ""
	@echo "Development (Local - Foreground):"
	@echo "  make dev-backend        - Run backend locally (Ctrl+C to stop)"
	@echo "  make dev-frontend       - Run frontend locally (Ctrl+C to stop)"
	@echo ""
	@echo "Development (Local - Background):"
	@echo "  make dev-up             - Start backend + frontend in background"
	@echo "  make dev-down           - Stop all local dev processes"
	@echo "  make dev-backend-up     - Start backend in background"
	@echo "  make dev-backend-down   - Stop backend"
	@echo "  make dev-frontend-up    - Start frontend in background"
	@echo "  make dev-frontend-down  - Stop frontend"
	@echo "  make dev-status         - Show running dev processes"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs           - View logs from all services"
	@echo "  make logs-backend   - View backend logs"
	@echo "  make logs-frontend  - View frontend logs"
	@echo "  make logs-db        - View database logs"
	@echo "  make status         - Show service status"
	@echo ""
	@echo "Database:"
	@echo "  make db-up          - Start only database container"
	@echo "  make db-down        - Stop only database container"
	@echo "  make db-shell       - Connect to PostgreSQL shell"
	@echo "  make db-reset       - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests"
	@echo "  make test-frontend  - Run frontend tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make clean-all      - Remove everything (containers, volumes, images)"
	@echo ""
	@echo "Services will be available at:"
	@echo "  Frontend:  http://localhost:${FRONTEND_EXTERNAL_PORT}"
	@echo "  Backend:   http://localhost:${BACKEND_EXTERNAL_PORT}"
	@echo "  API Docs:  http://localhost:${BACKEND_EXTERNAL_PORT}/docs"
	@echo "  Database:  localhost:${POSTGRES_EXTERNAL_PORT}"

setup:
	@echo "Setting up Simandaya Web..."
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env file"; else echo ".env already exists"; fi
	@echo "Setup complete! Edit .env if needed, then run 'make up'"

up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo ""
	@echo "Services started!"
	@echo "  Frontend:  http://localhost:${FRONTEND_EXTERNAL_PORT}"
	@echo "  Backend:   http://localhost:${BACKEND_EXTERNAL_PORT}/docs"
	@echo ""
	@echo "Run 'make logs' to view logs"

down:
	@echo "Stopping all services..."
	docker-compose down

restart:
	@echo "Restarting all services..."
	docker-compose restart

build:
	@echo "Building Docker images..."
	docker-compose build

rebuild:
	@echo "Rebuilding and restarting..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres-db

status:
	docker-compose ps

# Database commands
db-up:
	@echo "Starting database..."
	docker-compose up -d postgres-db
	@echo "Database started on port ${POSTGRES_EXTERNAL_PORT}"
	@echo "Waiting for database to be ready..."
	@sleep 3
	@docker-compose exec postgres-db pg_isready -U ${DB_USER} && echo "Database is ready!" || echo "Database is starting..."

db-down:
	@echo "Stopping database..."
	docker-compose stop postgres-db
	@echo "Database stopped"

db-shell:
	docker-compose exec postgres-db psql -U ${DB_USER} -d ${DB_NAME}

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres-db; \
		echo "Database reset complete"; \
	fi

# Local development - Foreground (Ctrl+C to stop)
dev-backend: _ensure-db
	@echo "Starting backend locally (foreground)..."
	@echo "DEV_MODE: DB drops and recreates on every reload"
	@echo "Press Ctrl+C to stop"
	@cd backend && \
	if [ ! -d venv ]; then \
		echo "Creating virtual environment..."; \
		python -m venv venv; \
	fi && \
	. venv/bin/activate && \
	pip install -q -r requirements.txt && \
	DEV_MODE=true DB_HOST=localhost DB_PORT=${POSTGRES_EXTERNAL_PORT} \
	uvicorn app.main:app --reload --host 0.0.0.0 --port ${APP_PORT}

dev-frontend:
	@echo "Starting frontend locally (foreground)..."
	@echo "Press Ctrl+C to stop"
	@cd frontend && \
	if [ ! -d node_modules ]; then \
		echo "Installing dependencies..."; \
		pnpm install; \
	fi && \
	pnpm dev

# Local development - Background mode
dev-up: dev-backend-up dev-frontend-up
	@echo ""
	@echo "[OK]All dev services started in background!"
	@echo "  Frontend:  http://localhost:${FRONTEND_EXTERNAL_PORT}"
	@echo "  Backend:   http://localhost:${APP_PORT}"
	@echo "  API Docs:  http://localhost:${APP_PORT}/docs"
	@echo ""
	@echo "Use 'make dev-status' to check status"
	@echo "Use 'make dev-down' to stop all"

dev-down: dev-backend-down dev-frontend-down
	@echo "[OK]All dev processes stopped"

dev-backend-up: _ensure-db
	@echo "Starting backend in background..."
	@if [ -f .backend.pid ] && kill -0 $$(cat .backend.pid) 2>/dev/null; then \
		echo "Backend already running (PID: $$(cat .backend.pid))"; \
		exit 1; \
	fi
	@cd backend && \
	if [ ! -d venv ]; then \
		echo "Creating virtual environment..."; \
		python -m venv venv; \
	fi && \
	. venv/bin/activate && \
	pip install -q -r requirements.txt && \
	DEV_MODE=true DB_HOST=localhost DB_PORT=${POSTGRES_EXTERNAL_PORT} \
	nohup uvicorn app.main:app --reload --host 0.0.0.0 --port ${APP_PORT} > ../logs/backend.log 2>&1 & \
	echo $$! > ../.backend.pid
	@sleep 2
	@if [ -f .backend.pid ] && kill -0 $$(cat .backend.pid) 2>/dev/null; then \
		echo "[OK]Backend started (PID: $$(cat .backend.pid))"; \
		echo "   Logs: logs/backend.log"; \
		echo "   URL: http://localhost:${APP_PORT}"; \
	else \
		echo "[ERR]Backend failed to start. Check logs/backend.log"; \
		rm -f .backend.pid; \
		exit 1; \
	fi

dev-backend-down:
	@if [ -f .backend.pid ]; then \
		PID=$$(cat .backend.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			echo "Stopping backend (PID: $$PID)..."; \
			kill $$PID 2>/dev/null || true; \
			sleep 1; \
			kill -9 $$PID 2>/dev/null || true; \
			echo "[OK]Backend stopped"; \
		else \
			echo "Backend not running"; \
		fi; \
		rm -f .backend.pid; \
	else \
		echo "No backend PID file found"; \
	fi

dev-frontend-up:
	@echo "Starting frontend in background..."
	@if [ -f .frontend.pid ] && kill -0 $$(cat .frontend.pid) 2>/dev/null; then \
		echo "[ERR]Frontend already running (PID: $$(cat .frontend.pid))"; \
		exit 1; \
	fi
	@cd frontend && \
	if [ ! -d node_modules ]; then \
		echo "Installing dependencies..."; \
		pnpm install; \
	fi && \
	nohup pnpm dev > ../logs/frontend.log 2>&1 & \
	echo $$! > ../.frontend.pid
	@sleep 3
	@if [ -f .frontend.pid ] && kill -0 $$(cat .frontend.pid) 2>/dev/null; then \
		echo "[OK]Frontend started (PID: $$(cat .frontend.pid))"; \
		echo "   Logs: logs/frontend.log"; \
		echo "   URL: http://localhost:${FRONTEND_EXTERNAL_PORT}"; \
	else \
		echo "[ERR]Frontend failed to start. Check logs/frontend.log"; \
		rm -f .frontend.pid; \
		exit 1; \
	fi

dev-frontend-down:
	@if [ -f .frontend.pid ]; then \
		PID=$$(cat .frontend.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			echo "Stopping frontend (PID: $$PID)..."; \
			kill $$PID 2>/dev/null || true; \
			sleep 1; \
			kill -9 $$PID 2>/dev/null || true; \
			echo "[OK]Frontend stopped"; \
		else \
			echo "Frontend not running"; \
		fi; \
		rm -f .frontend.pid; \
	else \
		echo "No frontend PID file found"; \
	fi

dev-status:
	@echo "Local Development Status:"
	@echo "========================="
	@if [ -f .backend.pid ] && kill -0 $$(cat .backend.pid) 2>/dev/null; then \
		echo "[OK]Backend:  Running (PID: $$(cat .backend.pid)) - http://localhost:${APP_PORT}"; \
	else \
		echo "[ERR]Backend:  Not running"; \
		rm -f .backend.pid 2>/dev/null || true; \
	fi
	@if [ -f .frontend.pid ] && kill -0 $$(cat .frontend.pid) 2>/dev/null; then \
		echo "[OK]Frontend: Running (PID: $$(cat .frontend.pid)) - http://localhost:${FRONTEND_EXTERNAL_PORT}"; \
	else \
		echo "[ERR]Frontend: Not running"; \
		rm -f .frontend.pid 2>/dev/null || true; \
	fi
	@echo ""
	@echo "Database:"
	@if docker ps --format '{{.Names}}' | grep -q simandaya-postgres; then \
		echo "[OK]Database: Running (Docker) - localhost:${POSTGRES_EXTERNAL_PORT}"; \
	else \
		echo "[ERR]Database: Not running (use 'make db-up')"; \
	fi

# Internal helpers
_ensure-db:
	@if ! docker ps --format '{{.Names}}' | grep -q simandaya-postgres; then \
		echo "Database not running, starting..."; \
		docker-compose up -d postgres-db; \
		echo "Waiting for database to be ready..."; \
		sleep 3; \
		docker-compose exec postgres-db pg_isready -U ${DB_USER} && echo "Database ready" || echo "Database starting..."; \
	else \
		echo "Database already running"; \
	fi

# Testing
test:
	@echo "Running all tests..."
	@make test-backend
	@make test-frontend

test-backend:
	@echo "Running backend tests..."
	@cd backend && \
	if [ -d venv ]; then \
		. venv/bin/activate && pytest; \
	else \
		echo "Backend venv not found. Run 'make dev-backend' first"; \
	fi

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && \
	if [ -d node_modules ]; then \
		pnpm test; \
	else \
		echo "Frontend node_modules not found. Run 'make dev-frontend' first"; \
	fi

# Cleanup
clean:
	@echo "Removing containers and volumes..."
	docker-compose down -v

clean-all:
	@echo "Removing containers, volumes, and images..."
	docker-compose down -v --rmi all
	@echo "Cleanup complete!"

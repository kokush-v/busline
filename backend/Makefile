.PHONY: help install run dev test lint format clean migrations migrate downgrade

help:
	@echo "🚀 Busline Backend Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install project dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Run development server"
	@echo "  make run              - Run production server"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          - Run database migrations (upgrade to latest)"
	@echo "  make migrate-create   - Create new migration"
	@echo "  make migrate-downgrade - Downgrade one migration"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-feature     - Run tests for specific feature (FEATURE=city)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Check code style (ruff) TODO: Implement ruff configuration"
	@echo "  make format           - Format code (ruff) TODO: Implement ruff configuration"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Remove cache files and directories"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	poetry install

dev:
	@echo "🔨 Starting development server..."
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --no-access-log

run:
	@echo "🚀 Starting production server..."
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log
migrate:
	@echo "🗄️  Running database migrations..."
	poetry run alembic upgrade head

migrate-create:
	@echo "✨ Create new migration (provide message via MESSAGE=your_message)"
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Error: MESSAGE not provided. Use: make migrate-create MESSAGE='your message'"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

migrate-downgrade:
	@echo "⬅️  Rolling back one migration..."
	poetry run alembic downgrade -1

test:
	@echo "🧪 Running all tests..."
	poetry run pytest tests/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	poetry run pytest tests/integration/ -v

test-unit:
	@echo "🧪 Running unit tests..."
	poetry run pytest tests/unit/ -v

test-feature:
	@echo "🧪 Running tests for feature: $(FEATURE)..."
	@if [ -z "$(FEATURE)" ]; then \
		echo "Error: FEATURE not provided. Use: make test-feature FEATURE=city"; \
		exit 1; \
	fi
	poetry run pytest tests/integration/features/$(FEATURE)/ tests/unit/features/$(FEATURE)/ -v

lint:
	@echo "🔍 Checking code style..."
	@echo "TODO: Implement ruff configuration"
	poetry run ruff check app/

format:
	@echo "✨ Formatting code..."
	@echo "TODO: Implement ruff configuration"
	poetry run ruff check app/ --fix
	poetry run ruff format app/

clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .env.local
	@echo "✅ Cache cleaned"

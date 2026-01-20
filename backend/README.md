# BusLine Backend

FastAPI-based backend for city bus management system.

## Installation

### Requirements

- Python >= 3.12
- Poetry

### Setup Command

```bash
make install
```

This will install all project dependencies via Poetry.

## Make Commands

To view all available commands, run:

```bash
make help
```

### Setup

| Command        | Description                  |
| -------------- | ---------------------------- |
| `make install` | Install project dependencies |

### Development

| Command    | Description                                                |
| ---------- | ---------------------------------------------------------- |
| `make dev` | Run dev server on `http://localhost:8000` with auto-reload |
| `make run` | Run production server on `http://localhost:8000`           |

### Database

| Command                             | Description                                    |
| ----------------------------------- | ---------------------------------------------- |
| `make migrate`                      | Run all pending migrations (upgrade to latest) |
| `make migrate-create MESSAGE='...'` | Create a new migration with message            |
| `make migrate-downgrade`            | Rollback one migration                         |

**Examples:**

```bash
make migrate-create MESSAGE='add_city_model'
```

### Testing

| Command                            | Description                      |
| ---------------------------------- | -------------------------------- |
| `make test`                        | Run all tests                    |
| `make test-integration`            | Run integration tests            |
| `make test-unit`                   | Run unit tests                   |
| `make test-feature FEATURE=<name>` | Run tests for a specific feature |

**Examples:**

```bash
make test                           # All tests
make test-integration               # Integration tests
make test-unit                      # Unit tests
make test-feature FEATURE=city      # Tests for 'city' feature
```

### Code Quality

| Command       | Description                 |
| ------------- | --------------------------- |
| `make lint`   | Check code style using Ruff |
| `make format` | Format code using Ruff      |

### Utilities

| Command      | Description                                                       |
| ------------ | ----------------------------------------------------------------- |
| `make clean` | Clean cache files (`__pycache__`, `.pytest_cache`, `.ruff_cache`) |

## Project Structure

```
app/
├── __init__.py
├── app.py                 # FastAPI Application
├── config/
│   ├── logging_config.py  # Logging configuration
├── core/
│   └── roles.py           # User roles
├── database/
│   └── db.py              # Database configuration
├── features/              # Business logic
│   └── city/
│       ├── models.py      # SQLAlchemy models
│       ├── route.py       # API routes
│       ├── schemas.py     # Pydantic schemas
│       └── service.py     # Business logic
├── log/
│   └── logger_service.py  # Logging service
└── settings/
    └── env.py             # Environment configuration

tests/
├── conftest.py            # Pytest config and global fixtures
├── integration/           # Integration tests
│   └── features/city/
│       └── test_routes.py
└── unit/                  # Unit tests
    └── features/city/
        └── test_schemas.py
```

## Technologies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pytest** - Testing framework
- **Ruff** - Code formatter and linter
- **Pydantic** - Data validation

## Development

### Running Dev Server

```bash
make dev
```

Server will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Test Architecture

The project uses a two-level test architecture:

- **Integration tests** (`tests/integration/`) - testing API endpoints and routes
- **Unit tests** (`tests/unit/`) - testing individual components (schemas, services)

Both test types use in-memory SQLite database for isolated testing.

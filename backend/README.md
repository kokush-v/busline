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
├── main.py                    # FastAPI application factory
├── core/                      # Core utilities (roles, S3 service, etc.)
├── database/                  # Database configuration
├── features/                  # Feature modules (city, bus, etc.)
├── logging/                   # Logging setup
├── middlewares/               # Middleware components
└── settings/                  # Environment configuration

tests/
├── conftest.py                # Pytest config and global fixtures
├── integration/               # Integration tests by feature
└── unit/                      # Unit tests by feature
```

## Technologies

- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy 2.0** - ORM with async support and type annotations
- **Alembic** - Database migrations
- **Pytest** - Testing framework
- **Ruff** - Fast linter and formatter (not implemented yet)
- **Pydantic** - Data validation with type hints
- **PostgreSQL** - Primary database
- **Uvicorn** - ASGI server

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

## Guidelines

### Model Rules

- **Typed columns:** Use SQLAlchemy 2.0 annotations (`Mapped[T]` + `mapped_column`).
- **Primary keys:** Prefer `uuid.UUID` with PostgreSQL `UUID(as_uuid=True)` and `default=uuid.uuid4`.
- **Timestamps:** Use `DateTime(timezone=True)` with `server_default=func.now()`; `onupdate=func.now()` for `updated_at`.
- **Constraints:** Add `unique=True`, `nullable=False` where applicable; enforce domain constraints in Pydantic schemas.
- **Naming:** Table names in plural (e.g., `cities`), snake_case columns.
- **Pydantic alignment:** Mirror model fields in schemas; use `Annotated` + `Field` for validation (e.g., longitude/latitude ranges).

Example:

```python
from typing import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, String, Float, func
import uuid

class City(Base):
    __tablename__ = "cities"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    longitude: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### DB Query Rules

- **Async-first:** Use `AsyncSession` for all DB operations.
- **Core-style DML:** Prefer explicit `insert()`, `update()`, `delete()` for mutations; use `.returning(Model)` to fetch affected rows.
- **Selects:** Use `select(Model).where(...)`; avoid loading unrelated rows.
- **Conflicts:** Check for unique conflicts before insert (e.g., name uniqueness) and raise appropriate HTTP errors in services.
- **Transactions:** Commit after mutation; group related writes in a single transaction when possible.
- **Refreshing:** With Core-style DML + `returning`, no need for `session.refresh()`.
- **Filtering:** Always include explicit `where` clauses (`Model.id == id`) to scope operations.

Examples:

```python
from sqlalchemy import select, insert, update, delete

# Create
stmt = insert(City).values(**payload.model_dump()).returning(City)
city = (await session.execute(stmt)).scalars().one()
await session.commit()

# Update
stmt = update(City).where(City.id == city_id).values(**update_data).returning(City)
city = (await session.execute(stmt)).scalars().one()
await session.commit()

# Delete
await session.execute(delete(City).where(City.id == city_id))
await session.commit()
```

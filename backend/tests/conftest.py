from collections.abc import AsyncGenerator, Generator
import os
import pathlib
from typing import Any

from alembic.command import downgrade, upgrade
from alembic.config import Config as AlembicConfig
import boto3
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.settings.env import get_env_settings
from tests.dependencies import override_app_test_dependencies, override_dependency

TEST_HOST = 'http://test'

# AWS test configuration
TEST_AWS_REGION = 'us-east-1'
TEST_S3_PHOTOS_BUCKET = 'test-photos-bucket'
TEST_S3_THUMBNAILS_BUCKET = 'test-thumbnails-bucket'


def pytest_configure(config: pytest.Config) -> None:
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    os.environ['ENVIRONMENT'] = 'test'
    # Configure AWS settings for moto
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_REGION'] = TEST_AWS_REGION
    os.environ['S3_PHOTOS_BUCKET'] = TEST_S3_PHOTOS_BUCKET
    os.environ['S3_THUMBNAILS_BUCKET'] = TEST_S3_THUMBNAILS_BUCKET


@pytest.fixture(scope='session')
async def app() -> AsyncGenerator[FastAPI, Any]:
    from app.main import get_application

    _app = get_application(include_middlewares=False)
    override_app_test_dependencies(_app)

    yield _app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST) as client:
        yield client


@pytest.fixture(scope='function')
async def session(app: FastAPI, _engine: AsyncEngine) -> AsyncGenerator[AsyncSession, Any]:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_factory = async_sessionmaker(connection, expire_on_commit=False)
    session = session_factory()

    from app.database.db import get_db_session

    override_dependency(app, get_db_session, lambda: session)

    try:
        yield session
    finally:
        await trans.rollback()
        await session.close()
        await connection.close()


@pytest.fixture(scope='session')
async def _engine(_run_migrations: None) -> AsyncGenerator[AsyncEngine, Any]:
    settings = get_env_settings()
    # Use psycopg instead of asyncpg for async engine (psycopg supports async)
    db_url = settings.DATABASE_URL.replace('+asyncpg', '+psycopg')

    engine = create_async_engine(db_url)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope='session')
def _run_migrations(_postgres_container: PostgresContainer) -> Generator[None, Any, None]:
    """Run migrations synchronously before tests."""
    settings = get_env_settings()
    # Use sync psycopg for migrations
    sync_url = settings.DATABASE_URL.replace('+asyncpg', '')

    alembic_config = AlembicConfig()
    alembic_config.set_main_option('script_location', find_migrations_script_location())
    alembic_config.set_main_option('sqlalchemy.url', sync_url)

    # Run migrations
    downgrade(alembic_config, 'base')
    upgrade(alembic_config, 'head')

    yield

    # Cleanup after tests
    downgrade(alembic_config, 'base')


@pytest.fixture(scope='session', autouse=True)
def _postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer(
        image='postgres:latest', username='test_busline', password='test_busline', dbname='TestBusLine'
    ) as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        # Use psycopg driver (supports both sync and async)
        os.environ['DATABASE_URL'] = (
            f'postgresql+asyncpg://{postgres.username}:{postgres.password}@{host}:{port}/{postgres.dbname}'
        )
        get_env_settings.cache_clear()
        yield postgres


def find_migrations_script_location() -> str:
    """Help find script location if tests were run by debugger or any other way except writing 'pytest' in cli"""
    return os.path.join(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent, 'migrations')


@pytest.fixture(scope='session', autouse=True)
def _aws_mock():
    """Mock AWS services using moto for the entire test session."""
    with mock_aws():
        # Create test S3 buckets
        s3_client = boto3.client('s3', region_name=TEST_AWS_REGION)
        s3_client.create_bucket(Bucket=TEST_S3_PHOTOS_BUCKET)
        s3_client.create_bucket(Bucket=TEST_S3_THUMBNAILS_BUCKET)

        # Clear S3Service cache so it picks up mocked AWS
        from app.core.aws.s3_service import get_s3_service

        get_s3_service.cache_clear()

        yield

        get_s3_service.cache_clear()

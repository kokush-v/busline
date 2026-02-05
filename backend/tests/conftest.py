from collections.abc import AsyncGenerator, Generator
import os
import pathlib
import time
from typing import Any
from unittest.mock import patch
from uuid import UUID

from alembic.command import downgrade, upgrade
from alembic.config import Config as AlembicConfig
import boto3
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
import pytest
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.features.auth.schemas import CognitoUser
from app.features.user.enums import UserRoleGroups
from app.settings.env import get_env_settings
from tests.dependencies import override_app_test_dependencies, override_dependency

TEST_HOST = 'http://test'

# AWS test configuration
TEST_AWS_REGION = 'us-east-1'
TEST_S3_PHOTOS_BUCKET = 'test-photos-bucket'
TEST_S3_THUMBNAILS_BUCKET = 'test-thumbnails-bucket'

# Test user ID (valid UUID)
TEST_USER_ID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'

# Test user for mocked authentication
TEST_COGNITO_USER = CognitoUser(
    sub=TEST_USER_ID,
    email='test@example.com',
    name='Test User',
    phone_number='+380123456789',
    cognito_groups=[UserRoleGroups.ADMIN, UserRoleGroups.USER],
    iat=int(time.time()),
    exp=int(time.time()) + 3600,
    aud='test-client-id',
    iss='https://cognito-idp.us-east-1.amazonaws.com/test-pool-id',
)


@pytest.fixture(scope='session', autouse=True)
def _mock_cognito_auth():
    """Mock Cognito authentication for all tests."""

    async def mock_verify_token(self, token: str) -> CognitoUser:
        return TEST_COGNITO_USER

    with patch('app.core.aws.cognito.CognitoService.verify_token', mock_verify_token):
        # Clear the cached cognito service so it picks up the mock
        from app.core.aws.cognito import get_cognito_service

        get_cognito_service.cache_clear()
        yield
        get_cognito_service.cache_clear()


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
    # Include Authorization header for endpoints that require authentication
    headers = {'Authorization': 'Bearer test-token'}
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST, headers=headers) as client:
        yield client


@pytest.fixture(scope='function')
async def session(app: FastAPI, _engine: AsyncEngine) -> AsyncGenerator[AsyncSession, Any]:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_factory = async_sessionmaker(connection, expire_on_commit=False)
    session = session_factory()

    from app.database.db import get_db_session
    from app.features.user.models import User

    override_dependency(app, get_db_session, lambda: session)

    # Create test user for authentication
    await session.execute(
        insert(User).values(
            id=UUID(TEST_USER_ID),
            email=TEST_COGNITO_USER.email,
            name=TEST_COGNITO_USER.name,
            role=UserRoleGroups.ADMIN,
        )
    )
    await session.flush()

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

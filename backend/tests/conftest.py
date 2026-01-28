import boto3
from httpx import ASGITransport, AsyncClient
from moto import mock_aws
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.s3_service import S3Service, get_s3_service
from app.database.db import Base, get_db_session
from app.main import app
from app.settings.env import Settings, get_env_settings


@pytest.fixture(scope='session')
def db_url():
    """Setup PostgreSQL testcontainer for the test session."""
    with PostgresContainer(
        image='postgres:16-alpine',
        username='test',
        password='test',
        dbname='test_db',
    ) as container:
        url = container.get_connection_url().replace('postgresql+psycopg2://', 'postgresql+asyncpg://', 1)

        yield url


@pytest_asyncio.fixture
async def db_engine(db_url):
    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={'server_settings': {'jit': 'off'}},
    )
    yield engine
    await engine.dispose()


@pytest.fixture
def mock_s3_setup():
    """Setup moto mock for S3."""
    with mock_aws():
        # Use synchronous boto3 to create buckets
        s3_client = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id='testing',
            aws_secret_access_key='testing',
        )
        s3_client.create_bucket(Bucket='photos')
        s3_client.create_bucket(Bucket='thumbnails')
        yield


@pytest_asyncio.fixture
async def s3_service(mock_s3_setup):
    """Create S3 service instance populated with test settings."""
    test_settings = Settings(
        AWS_ACCESS_KEY_ID='testing',
        AWS_SECRET_ACCESS_KEY='testing',
        AWS_REGION='us-east-1',
        S3_PHOTOS_BUCKET='photos',
        S3_THUMBNAILS_BUCKET='thumbnails',
        S3_PRESIGNED_URL_EXPIRATION=3600,
    )

    service = S3Service()
    service._settings = test_settings

    # Add synchronous client for tests that need direct S3 access
    service._s3_client = boto3.client(
        's3',
        region_name='us-east-1',
        aws_access_key_id='testing',
        aws_secret_access_key='testing',
    )

    return service


@pytest_asyncio.fixture(scope='function')
async def db_session(db_engine):
    """
    Creates tables before test and drops them after.
    Yields a fresh async session.
    """
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, s3_service: S3Service):
    """Async client with overrides."""

    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_s3_service] = lambda: s3_service
    app.dependency_overrides[get_env_settings] = lambda: s3_service._settings

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url='http://test') as test_client:
        yield test_client

    app.dependency_overrides.clear()

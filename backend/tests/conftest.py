import boto3
from httpx import AsyncClient
from moto import mock_s3
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.s3_service import S3Service, get_s3_service
from app.database.db import Base, get_db_session
from app.main import app
from app.settings.env import Settings, get_env_settings


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    """Setup PostgreSQL testcontainer for the test session (synchronous)"""
    global postgres_container

    postgres_container = PostgresContainer(
        image='postgres:16-alpine',
        username='test',
        password='test',
        dbname='test_db',
    )
    postgres_container.start()

    yield

    postgres_container.stop()


@pytest.fixture(scope='function')
def mock_s3_setup():
    """Setup moto mock for S3 in each test - entire scope"""
    with mock_s3():
        # Create S3 client and buckets
        client = boto3.client(
            's3',
            aws_access_key_id='testing',
            aws_secret_access_key='testing',
            region_name='us-east-1',
        )

        # Create test buckets
        client.create_bucket(Bucket='photos')
        client.create_bucket(Bucket='thumbnails')

        yield


@pytest.fixture
def s3_service(mock_s3_setup):
    """Create S3 service instance for testing with moto mock"""
    # Override settings for test environment
    test_settings = Settings(
        AWS_ACCESS_KEY_ID='testing',
        AWS_SECRET_ACCESS_KEY='testing',
        AWS_REGION='us-east-1',
        S3_PHOTOS_BUCKET='photos',
        S3_THUMBNAILS_BUCKET='thumbnails',
        S3_PRESIGNED_URL_EXPIRATION=3600,
    )

    # Create S3 service with moto mock (inside the mock context)
    s3_service = S3Service()
    s3_service._settings = test_settings
    s3_service._s3_client = boto3.client(
        's3',
        aws_access_key_id='testing',
        aws_secret_access_key='testing',
        region_name='us-east-1',
    )

    return s3_service


@pytest_asyncio.fixture(scope='function')
async def db_session():
    """Create an async database session for each test"""
    db_url = postgres_container.get_connection_url()
    db_url = db_url.replace('postgresql+psycopg2://', 'postgresql+asyncpg://', 1)

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        connect_args={'timeout': 10, 'server_settings': {'jit': 'off'}},
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        async with async_session_maker() as session:
            yield session
    finally:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            pass
        finally:
            await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, s3_service: S3Service):
    """Create async test client with overridden database and S3 dependencies"""

    async def override_get_db():
        yield db_session

    def override_get_s3():
        return s3_service

    def override_get_settings():
        return s3_service._settings

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_s3_service] = override_get_s3
    app.dependency_overrides[get_env_settings] = override_get_settings

    async with AsyncClient(app=app, base_url='http://test') as test_client:
        yield test_client

    app.dependency_overrides.clear()

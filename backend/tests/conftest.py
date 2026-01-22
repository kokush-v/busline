from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.database.db import Base, get_db_session
from app.main import app


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
async def client(db_session: AsyncSession):
    """Create async test client with overridden database dependency"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(app=app, base_url='http://test') as test_client:
        yield test_client

    app.dependency_overrides.clear()

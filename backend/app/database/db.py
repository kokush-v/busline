from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache

from alembic.config import Config as AlembicConfig
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.settings.env import get_env_settings

POSTGRES_INDEXES_NAMING_CONVENTION = {
    'ix': '%(column_0_label)s_idx',
    'uq': '%(table_name)s_%(column_0_name)s_key',
    'ck': '%(table_name)s_%(constraint_name)s_check',
    'fk': '%(table_name)s_%(column_0_name)s_fkey',
    'pk': '%(table_name)s_pkey',
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.url = self._make_async_url(url)

        self.engine: AsyncEngine = create_async_engine(
            self.url,
            echo=echo,
        )

        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def _make_async_url(self, url: str) -> str:
        if url.startswith('postgresql://') and '+asyncpg' not in url:
            return url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return url

    def get_db_url(self) -> str:
        return self.url

    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


@lru_cache
def get_database_helper() -> DatabaseHelper:
    settings = get_env_settings()

    return DatabaseHelper(
        url=settings.DATABASE_URL,
        echo=settings.DEBUG,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db_helper = get_database_helper()
    async with db_helper.session_scope() as session:
        yield session


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get async session maker for background tasks."""
    db_helper = get_database_helper()
    return db_helper.session_factory


def get_alembic_config(database_url: str, script_location: str = 'migrations') -> AlembicConfig:
    """Create alembic config for running migrations programmatically.

    Args:
        database_url: Database URL (sync psycopg URL expected)
        script_location: Path to migrations directory

    Returns:
        Configured AlembicConfig instance
    """
    alembic_config = AlembicConfig()
    alembic_config.set_main_option('script_location', script_location)
    alembic_config.set_main_option('sqlalchemy.url', database_url)
    return alembic_config

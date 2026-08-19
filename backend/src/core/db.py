"""Motor y sesión de base de datos (SQLAlchemy 2.0 async)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(_settings.database_url, echo=False, pool_pre_ping=True)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI: una sesión de BD por request."""
    async with SessionLocal() as session:
        yield session

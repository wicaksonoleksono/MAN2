from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from typing import AsyncGenerator
from app.config.settings import settings


class Base(AsyncAttrs, DeclarativeBase):
    """
    Base model for all database models

    Inherits from:
    - AsyncAttrs: Enables async attribute loading
    - DeclarativeBase: SQLAlchemy 2.0 declarative base
    """
    pass


# Global async engine (created once, reused across requests)
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.DB_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# Global session factory (created once, generates sessions per request)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions

    Creates a new session per request, handles commits/rollbacks automatically.

    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session for the request
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables (run on startup)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections (run on shutdown)"""
    await engine.dispose()

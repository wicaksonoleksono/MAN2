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


async def init_db(drop_existing: bool = False):
    """
    Initialize database tables (run on startup)

    Args:
        drop_existing: If True, drops all tables before creating (DEV ONLY!)
    """
    # Import all models to register them with Base.metadata
    from app.models.user import User  # noqa: F401
    from app.models.siswa_profile import SiswaProfile  # noqa: F401
    from app.models.guru_profile import GuruProfile  # noqa: F401
    from app.models.absensi import Absensi  # noqa: F401
    from app.models.izin_keluar import IzinKeluar  # noqa: F401
    from app.models.tahun_ajaran import TahunAjaran  # noqa: F401
    from app.models.semester import Semester  # noqa: F401
    from app.models.kalender_akademik import KalenderAkademik  # noqa: F401
    from app.models.mata_pelajaran import MataPelajaran  # noqa: F401
    from app.models.slot_waktu import SlotWaktu  # noqa: F401
    from app.models.kelas import Kelas  # noqa: F401
    from app.models.siswa_kelas import SiswaKelas  # noqa: F401
    from app.models.guru_mapel import GuruMapel  # noqa: F401
    from app.models.jadwal import Jadwal  # noqa: F401

    async with engine.begin() as conn:
        if drop_existing:
            print("WARNING: Dropping all existing tables...")
            await conn.run_sync(Base.metadata.drop_all)

        print("Creating/updating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully")


async def close_db():
    """Close database connections (run on shutdown)"""
    await engine.dispose()

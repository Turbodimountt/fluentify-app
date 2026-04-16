"""
Fluentify Backend — Database Configuration
SQLAlchemy 2.0 async engine with PostgreSQL (asyncpg).
Falls back to SQLite for development when DATABASE_URL is not set.
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Determine database URL — fall back to async SQLite for local dev
_db_url = settings.database_url
if not _db_url or _db_url == "postgresql+asyncpg://" or "YOUR_DB_PASSWORD" in _db_url:
    _db_url = "sqlite+aiosqlite:///./fluentify_dev.db"
    _engine_kwargs = {"echo": settings.debug}
else:
    # Transformation: If using Supabase Pooler (6543), switch to Direct Connection (5432)
    # This solves the DuplicatePreparedStatementError permanently.
    if "pooler.supabase.com:6543" in _db_url:
        # Extract project ref from the current host (e.g., postgres.REF@host)
        try:
            _db_url = _db_url.replace(":6543", ":5432")
            _db_url = _db_url.replace("aws-1-us-east-2.pooler.supabase.com", "db.ogdemdghhuntuuxvopdd.supabase.co")
        except:
            pass
    
    _engine_kwargs = {
        "echo": settings.debug,
        "pool_size": 10,
        "max_overflow": 5,
        "pool_pre_ping": True,
    }

engine = create_async_engine(_db_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def init_db():
    """Create all tables (only for SQLite dev mode).
    For PostgreSQL/Supabase, tables are created via migrations.
    """
    if "sqlite" in str(engine.url):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    """Dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

"""Database configuration and connection setup."""
import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.config.settings import settings


class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
    
    def create_engine(self) -> AsyncEngine:
        """Create async database engine with connection pool."""
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_MAX,
            max_overflow=0,
            pool_pre_ping=True,
            poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
        )
    
    async def init_db(self) -> None:
        """Initialize database connection and create tables."""
        try:
            # Try the configured database URL first
            self.engine = self.create_engine()
            self.session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # Import models to ensure they're registered
            from src.models.base import Base
            from src.models.claim import Claim  # noqa: F401
            
            # Test database connection
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print(f"✅ Database connected successfully! Using: {settings.DATABASE_URL.split('@')[0]}@***")
                
        except Exception as e:
            print(f"⚠️  Primary database connection failed: {e}")
            
            # Try SQLite fallback if enabled
            if settings.USE_SQLITE_FALLBACK and "postgresql" in settings.DATABASE_URL:
                try:
                    print("🔄 Attempting SQLite fallback for development...")
                    sqlite_url = "sqlite+aiosqlite:///./claims_dev.db"
                    
                    # Create SQLite engine
                    from sqlalchemy.ext.asyncio import create_async_engine
                    self.engine = create_async_engine(
                        sqlite_url,
                        echo=settings.DB_ECHO,
                        poolclass=NullPool,
                    )
                    
                    self.session_factory = async_sessionmaker(
                        bind=self.engine,
                        class_=AsyncSession,
                        expire_on_commit=False,
                    )
                    
                    # Import models and create tables
                    from src.models.base import Base
                    from src.models.claim import Claim  # noqa: F401
                    
                    async with self.engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                        print("✅ SQLite fallback database initialized successfully!")
                        print("   Note: Using local SQLite for development. Data will be stored in claims_dev.db")
                        
                except Exception as sqlite_error:
                    print(f"❌ SQLite fallback also failed: {sqlite_error}")
                    print("   The application will start but database features will be unavailable.")
            else:
                print("   The application will start but database features will be unavailable.")
                print("   Please ensure PostgreSQL is running and check your DATABASE_URL setting.")
    
    async def close_db(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()


# Global database instance
db_config = DatabaseConfig()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    Yields:
        AsyncSession: Database session for the request.
    """
    if not db_config.session_factory:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable. Please check your database connection."
        )
    
    async with db_config.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - convenience function."""
    await db_config.init_db()


async def close_db() -> None:
    """Close database - convenience function."""
    await db_config.close_db()
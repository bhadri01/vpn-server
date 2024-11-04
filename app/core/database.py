from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Update this to your actual database URL

def create_engine(url, **kwargs):
    """Create an asynchronous SQLAlchemy engine."""
    return create_async_engine(url, echo=False, **kwargs)

# Create the database engine
engine = create_engine(DATABASE_URL)

# Async session factories
SessionLocal = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False)

# Create a base class for declarative class definitions
Base = declarative_base()

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
"""
Database initialization script
Run with: python -m app.core.init_db
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.models import (
    User,
    CraftsmanProfile,
    Trade,
    ServiceArea,
    Portfolio,
    Booking,
    Review,
    Payment,
    Message,
    MessageThread,
)


async def init_database():
    """Initialize database tables"""
    print("Initializing database...")

    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Drop all tables (use with caution in production!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()

    print("✅ Database initialization completed!")


if __name__ == "__main__":
    asyncio.run(init_database())

import asyncio
import sys
import os

from app.core.loggers import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base

async def init_db():
    logger("Initializing Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger("Database Initialized Successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())

import asyncio
import sys
import os
sys.path.append(os.path.abspath("."))
from app.core.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'media_assets'"))
        columns = [row[0] for row in res.fetchall()]
        print(f"Columns in media_assets: {columns}")

if __name__ == "__main__":
    asyncio.run(check())
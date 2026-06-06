import asyncio
import sys
import os
sys.path.append(os.path.abspath("."))
from app.core.database import engine
from sqlalchemy import text

async def run():
    async with engine.begin() as conn:
        statements = [
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS distance_level VARCHAR(20)",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS view_angle VARCHAR(50)",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS person_visible BOOLEAN",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS face_visible BOOLEAN",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS face_quality VARCHAR(20)",
            "ALTER TABLE media_assets ADD COLUMN IF NOT EXISTS target_person_id UUID",
        ]
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
                print(f"Executed: {stmt}")
            except Exception as e:
                print(f"Warning: {stmt} - {e}")
        print("Schema update completed")

if __name__ == "__main__":
    asyncio.run(run())
"""
Migration script to add original_title column to news_events table
"""
import asyncio
import logging
from sqlalchemy import text
from app.database import engine, async_session_maker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate():
    """Add original_title column if it doesn't exist"""
    async with engine.begin() as conn:
        # Check if column exists
        result = await conn.execute(
            text("PRAGMA table_info(news_events)")
        )
        columns = [row[1] for row in result.fetchall()]
        
        if 'original_title' in columns:
            logger.info("Column 'original_title' already exists. No migration needed.")
            return
        
        # Add the column
        logger.info("Adding 'original_title' column to news_events table...")
        await conn.execute(
            text("ALTER TABLE news_events ADD COLUMN original_title TEXT")
        )
        logger.info("✅ Migration complete! Column 'original_title' added successfully.")


async def main():
    logger.info("Starting database migration...")
    await migrate()
    logger.info("Migration finished.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())


"""
Background task scheduler for data collection
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def rss_scrape_job():
    """Scheduled job for RSS feeds scraping"""
    from app.services.rss_scraper import scrape_all_rss_feeds
    logger.info("🔄 Running RSS feeds scraper job...")
    try:
        total_saved = await scrape_all_rss_feeds(max_entries_first_run=10)
        logger.info(f"✅ RSS scraper job completed: {total_saved} events saved")
    except Exception as e:
        logger.error(f"❌ RSS scraper job failed: {e}")


async def db_cleanup_job():
    """Scheduled job for database cleanup"""
    from app.services.db_cleanup import cleanup_old_events
    logger.info("🗑️  Running database cleanup job...")
    try:
        await cleanup_old_events()
        logger.info("✅ Database cleanup job completed")
    except Exception as e:
        logger.error(f"❌ Database cleanup job failed: {e}")


async def start_scheduler():
    """Start the background task scheduler"""
    # Add RSS scraper job (every 5 minutes)
    scheduler.add_job(
        rss_scrape_job,
        trigger=IntervalTrigger(seconds=300),  # 5 minutes
        id="rss_scraper",
        name="RSS Feeds Scraper",
        replace_existing=True,
        max_instances=1
    )
    
    # Add database cleanup job (daily at 3 AM)
    scheduler.add_job(
        db_cleanup_job,
        trigger=IntervalTrigger(hours=24),  # Every 24 hours
        id="db_cleanup",
        name="Database Cleanup",
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.start()
    logger.info("📅 Scheduler started:")
    logger.info("   - RSS scraper: every 5 minutes")
    logger.info("   - Database cleanup: every 24 hours")
    
    # Run initial scrape after startup
    scheduler.add_job(rss_scrape_job, id="initial_rss", replace_existing=True)
    
    # Run initial cleanup after startup (in 1 minute to let DB initialize)
    from datetime import datetime, timedelta
    scheduler.add_job(
        db_cleanup_job, 
        trigger='date', 
        run_date=datetime.now() + timedelta(minutes=1),
        id="initial_cleanup", 
        replace_existing=True
    )


async def stop_scheduler():
    """Stop the background task scheduler"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("📅 Scheduler stopped")


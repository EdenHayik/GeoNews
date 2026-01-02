"""
Database cleanup service to maintain data retention policy
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import NewsEvent
from app.database import async_session_maker
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def cleanup_old_events():
    """
    Delete news events older than the configured retention period.
    Default: 30 days
    """
    try:
        retention_days = settings.data_retention_days
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        async with async_session_maker() as db:
            # Count events to be deleted
            count_query = select(NewsEvent).where(
                NewsEvent.timestamp_detected < cutoff_date
            )
            result = await db.execute(count_query)
            events_to_delete = len(result.scalars().all())
            
            if events_to_delete > 0:
                # Delete old events
                delete_query = delete(NewsEvent).where(
                    NewsEvent.timestamp_detected < cutoff_date
                )
                await db.execute(delete_query)
                await db.commit()
                
                logger.info(f"🗑️  Database cleanup: Deleted {events_to_delete} events older than {retention_days} days")
            else:
                logger.info(f"✅ Database cleanup: No events older than {retention_days} days found")
                
    except Exception as e:
        logger.error(f"❌ Error during database cleanup: {e}")
        raise


async def get_database_stats():
    """
    Get database statistics for monitoring
    """
    try:
        async with async_session_maker() as db:
            # Total events
            total_query = select(NewsEvent)
            total_result = await db.execute(total_query)
            total_events = len(total_result.scalars().all())
            
            # Events by age
            now = datetime.utcnow()
            day_ago = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            day_query = select(NewsEvent).where(NewsEvent.timestamp_detected >= day_ago)
            day_result = await db.execute(day_query)
            day_events = len(day_result.scalars().all())
            
            week_query = select(NewsEvent).where(NewsEvent.timestamp_detected >= week_ago)
            week_result = await db.execute(week_query)
            week_events = len(week_result.scalars().all())
            
            month_query = select(NewsEvent).where(NewsEvent.timestamp_detected >= month_ago)
            month_result = await db.execute(month_query)
            month_events = len(month_result.scalars().all())
            
            stats = {
                "total_events": total_events,
                "last_24h": day_events,
                "last_7d": week_events,
                "last_30d": month_events,
                "retention_days": settings.data_retention_days,
            }
            
            logger.info(f"📊 Database stats: {stats}")
            return stats
            
    except Exception as e:
        logger.error(f"❌ Error getting database stats: {e}")
        return None


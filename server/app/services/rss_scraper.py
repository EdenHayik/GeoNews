"""
RSS Feed Scraper Service
Fetches and processes news from RSS feeds using feedparser
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import feedparser

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.feeds_config import get_all_feeds
from app.database import async_session_maker
from app.models import NewsEvent, ScraperState
from app.services.ai_processor import process_news_text

logger = logging.getLogger(__name__)


def get_content_hash(text: str, url: str) -> str:
    """Generate a unique hash for content deduplication"""
    content = f"{text[:200]}_{url}"
    return hashlib.sha256(content.encode()).hexdigest()


async def save_event(db: AsyncSession, event_data: dict) -> bool:
    """Save a processed event to database, returns True if saved"""
    # Check for duplicate
    query = select(NewsEvent).where(NewsEvent.content_hash == event_data["content_hash"])
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        logger.debug(f"Duplicate event skipped: {event_data['content_hash'][:16]}...")
        return False
    
    event = NewsEvent(**event_data)
    db.add(event)
    await db.commit()
    logger.info(f"Saved RSS event: {event_data.get('original_title', event_data['summary_text'][:50])}...")
    return True


async def get_last_scrape_time(db: AsyncSession, source_name: str) -> Optional[datetime]:
    """Get the last scrape time for a source"""
    query = select(ScraperState).where(ScraperState.source_name == source_name)
    result = await db.execute(query)
    state = result.scalar_one_or_none()
    return state.last_run if state else None


async def update_scraper_state(db: AsyncSession, source_name: str, last_article_date: Optional[datetime] = None):
    """Update the scraper state with the newest article's publish date (or current time if none)"""
    query = select(ScraperState).where(ScraperState.source_name == source_name)
    result = await db.execute(query)
    state = result.scalar_one_or_none()
    
    # Use the newest article date if provided, otherwise use current time
    update_time = last_article_date if last_article_date else datetime.utcnow()
    
    if state:
        # Only update if the new time is newer than existing
        if state.last_run is None or update_time > state.last_run:
            state.last_run = update_time
    else:
        state = ScraperState(
            source_name=source_name,
            last_run=update_time
        )
        db.add(state)
    
    await db.commit()


def parse_rss_date(date_str: str) -> Optional[datetime]:
    """Parse RSS date string to datetime"""
    try:
        # feedparser returns time.struct_time
        if hasattr(date_str, 'timetuple'):
            return datetime(*date_str.timetuple()[:6])
        return None
    except Exception as e:
        logger.debug(f"Failed to parse date: {e}")
        return None


async def process_rss_entry(entry: Dict, feed_name: str, feed_url: str) -> Optional[dict]:
    """Process a single RSS entry"""
    try:
        # Extract title and content
        title = entry.get('title', '')
        
        # Try to get content from various fields
        content = ''
        if 'summary' in entry:
            content = entry.get('summary', '')
        elif 'description' in entry:
            content = entry.get('description', '')
        elif 'content' in entry:
            content_list = entry.get('content', [])
            if content_list and len(content_list) > 0:
                content = content_list[0].get('value', '')
        
        # Combine title and content for AI processing
        full_text = f"{title}\n\n{content}" if content else title
        
        # Skip if too short
        if len(full_text.strip()) < 20:
            logger.debug(f"Skipping short entry from {feed_name}")
            return None
        
        # Get AI processing result
        ai_result = await process_news_text(full_text, feed_name)
        
        if not ai_result:
            logger.debug(f"AI processing failed for RSS entry from {feed_name}")
            return None
        
        # Get publish date
        pub_date = None
        if 'published_parsed' in entry:
            pub_date = parse_rss_date(entry.published_parsed)
        elif 'updated_parsed' in entry:
            pub_date = parse_rss_date(entry.updated_parsed)
        
        # Get entry URL
        entry_url = entry.get('link', feed_url)
        
        # Build event data
        event_data = {
            "source_name": feed_name,
            "original_url": entry_url,
            "original_text": full_text[:2000],
            "original_title": ai_result.title,
            "summary_text": ai_result.summary,
            "location_name": ai_result.location_name,
            "latitude": ai_result.latitude,
            "longitude": ai_result.longitude,
            "category": ai_result.category,
            "confidence_score": ai_result.confidence_score,
            "image_url": None,  # Could extract from enclosures if needed
            "timestamp_detected": datetime.utcnow(),
            "timestamp_original": pub_date,
            "content_hash": get_content_hash(full_text, entry_url),
        }
        
        return event_data
        
    except Exception as e:
        logger.error(f"Error processing RSS entry from {feed_name}: {e}")
        return None


async def scrape_rss_feed(feed_name: str, feed_url: str, max_entries_first_run: int = 10) -> int:
    """
    Scrape a single RSS feed and save events
    - On first run: fetch up to max_entries_first_run articles
    - On subsequent runs: fetch all articles published since last scrape
    
    Returns number of events saved
    """
    logger.info(f"Scraping RSS feed: {feed_name} ({feed_url})")
    
    try:
        async with async_session_maker() as db:
            # Get last scrape time
            last_scrape = await get_last_scrape_time(db, feed_name)
            is_first_run = last_scrape is None
            
            if is_first_run:
                logger.info(f"First run for {feed_name} - fetching up to {max_entries_first_run} articles")
            else:
                logger.info(f"Fetching articles published after {last_scrape} for {feed_name}")
        
        # Parse RSS feed
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            logger.warning(f"RSS feed {feed_name} has parsing issues: {feed.bozo_exception}")
        
        entries = feed.entries
        
        if not entries:
            logger.warning(f"No entries found in RSS feed: {feed_name}")
            return 0
        
        logger.info(f"Found {len(entries)} total entries in {feed_name}")
        
        # Filter entries based on publish date
        entries_to_process = []
        
        if is_first_run:
            # First run: take up to N most recent entries
            entries_to_process = entries[:max_entries_first_run]
            logger.info(f"Processing {len(entries_to_process)} most recent entries (first run)")
        else:
            # Subsequent runs: only process entries newer than last scrape
            for entry in entries:
                pub_date = None
                if 'published_parsed' in entry:
                    pub_date = parse_rss_date(entry.published_parsed)
                elif 'updated_parsed' in entry:
                    pub_date = parse_rss_date(entry.updated_parsed)
                
                # If we can't determine publish date, include it to be safe
                # Or if it's newer than last scrape
                if pub_date is None or pub_date > last_scrape:
                    entries_to_process.append(entry)
            
            logger.info(f"Found {len(entries_to_process)} new entries since last scrape")
        
        if not entries_to_process:
            logger.info(f"No new entries to process for {feed_name}")
            async with async_session_maker() as db:
                # Still update scraper state to current time so we don't recheck the same empty feed
                await update_scraper_state(db, feed_name, datetime.utcnow())
            return 0
        
        # Track the newest article date
        newest_article_date = None
        
        events_saved = 0
        async with async_session_maker() as db:
            for entry in entries_to_process:
                # Track the newest publish date
                pub_date = None
                if 'published_parsed' in entry:
                    pub_date = parse_rss_date(entry.published_parsed)
                elif 'updated_parsed' in entry:
                    pub_date = parse_rss_date(entry.updated_parsed)
                
                if pub_date and (newest_article_date is None or pub_date > newest_article_date):
                    newest_article_date = pub_date
                
                event_data = await process_rss_entry(entry, feed_name, feed_url)
                
                if event_data:
                    if await save_event(db, event_data):
                        events_saved += 1
            
            # Update scraper state with the newest article date (or current time if none)
            await update_scraper_state(db, feed_name, newest_article_date)
        
        logger.info(f"RSS feed {feed_name}: {events_saved} new events saved")
        return events_saved
        
    except Exception as e:
        logger.error(f"Error scraping RSS feed {feed_name}: {e}")
        return 0


async def scrape_all_rss_feeds(max_entries_first_run: int = 10):
    """
    Scrape all configured RSS feeds
    - First run: fetch up to max_entries_first_run from each
    - Subsequent runs: fetch all new articles since last scrape
    
    Returns total number of events saved
    """
    logger.info("Starting RSS feeds scraping...")
    
    feeds = get_all_feeds()
    total_saved = 0
    
    for feed in feeds:
        try:
            saved = await scrape_rss_feed(
                feed["name"],
                feed["url"],
                max_entries_first_run
            )
            total_saved += saved
        except Exception as e:
            logger.error(f"Failed to scrape {feed['name']}: {e}")
            continue
    
    logger.info(f"RSS scraping complete: {total_saved} total events saved from {len(feeds)} feeds")
    return total_saved


async def test_single_feed(feed_name: str):
    """Test a single RSS feed"""
    feeds = get_all_feeds()
    feed = next((f for f in feeds if f["name"] == feed_name), None)
    
    if not feed:
        print(f"Feed '{feed_name}' not found")
        return
    
    print(f"\n=== Testing RSS Feed: {feed_name} ===")
    print(f"URL: {feed['url']}")
    print(f"Language: {feed['language']}")
    print(f"Category: {feed['category']}\n")
    
    saved = await scrape_rss_feed(feed["name"], feed["url"], max_entries_first_run=10)
    print(f"\n✅ Saved {saved} events from {feed_name}")


if __name__ == "__main__":
    import asyncio
    
    # Test with a single feed
    asyncio.run(test_single_feed("Ynet"))


"""
Daily Recap Generator
Generates AI-powered summaries of news events by source
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import NewsEvent
from app.services.ai_processor import client as openai_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

RECAP_SYSTEM_PROMPT = """You are an expert intelligence analyst creating daily news recaps for Middle Eastern geopolitical events.

Your task is to analyze a collection of news events from the past 24 hours and create a comprehensive, well-structured daily recap in HEBREW (עברית).

The recap should:
1. **Start with an executive summary** (2-3 sentences) highlighting the most significant developments
2. **Group events by theme/region** (e.g., Gaza operations, Lebanon border, political developments, etc.)
3. **Provide context and connections** between related events
4. **Highlight trends or patterns** if any emerge
5. **Maintain objectivity** and factual reporting
6. **Be written in clear, professional Hebrew**

Format your response as a structured report with:
- **כותרת ראשית** (Main headline/title - short and impactful)
- **סיכום מנהלים** (Executive summary paragraph)
- **התפתחויות עיקריות** (Main developments - organized by theme/region with bullet points)
- **מגמות ותובנות** (Trends and insights if applicable)

Return ONLY a JSON object with this structure:
{
  "title": "כותרת הסיכום היומי",
  "executive_summary": "פסקת סיכום מנהלים בעברית",
  "sections": [
    {
      "heading": "כותרת נושא/אזור",
      "items": [
        "פריט ראשון",
        "פריט שני"
      ]
    }
  ],
  "insights": "מגמות ותובנות (או null אם אין)",
  "total_events": 0,
  "time_range": "24 שעות אחרונות"
}"""


async def get_events_by_source(
    db: AsyncSession,
    source_name: str,
    hours: int = 24
) -> list[NewsEvent]:
    """Get all events for a specific source within time range"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = (
        select(NewsEvent)
        .where(NewsEvent.source_name == source_name)
        .where(NewsEvent.timestamp_detected >= cutoff_time)
        .order_by(NewsEvent.timestamp_detected.desc())
    )
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_available_sources(db: AsyncSession) -> list[dict]:
    """Get list of sources with event counts for last 24 hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=24)
    
    query = (
        select(
            NewsEvent.source_name,
            func.count(NewsEvent.id).label('event_count'),
            func.max(NewsEvent.timestamp_detected).label('latest_event')
        )
        .where(NewsEvent.timestamp_detected >= cutoff_time)
        .group_by(NewsEvent.source_name)
    )
    
    result = await db.execute(query)
    sources = []
    
    for row in result:
        sources.append({
            "source_name": row[0],
            "event_count": row[1],
            "latest_event": row[2].isoformat() if row[2] else None
        })
    
    return sources


async def generate_daily_recap(
    db: AsyncSession,
    source_name: str,
    hours: int = 24
) -> Optional[dict]:
    """Generate AI-powered daily recap for a specific source"""
    
    if not openai_client:
        logger.warning("OpenAI client not configured")
        return None
    
    # Get events for this source
    events = await get_events_by_source(db, source_name, hours)
    
    if not events:
        logger.info(f"No events found for {source_name} in last {hours} hours")
        return {
            "source_name": source_name,
            "hours": hours,
            "title": "לא נמצאו אירועים",
            "executive_summary": f"לא נמצאו אירועים עבור {source_name} ב-{hours} השעות האחרונות.",
            "sections": [],
            "insights": None,
            "total_events": 0,
            "time_range": f"{hours} שעות אחרונות",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    # Prepare events summary for AI
    events_text = []
    for i, event in enumerate(events, 1):
        event_summary = f"{i}. "
        if event.original_title:
            event_summary += f"{event.original_title} - "
        event_summary += f"{event.summary_text}"
        if event.location_name:
            event_summary += f" ({event.location_name})"
        event_summary += f" [קטגוריה: {event.category}]"
        events_text.append(event_summary)
    
    events_combined = "\n".join(events_text)
    
    user_message = f"""מקור: {source_name}
טווח זמן: {hours} שעות אחרונות
מספר אירועים: {len(events)}

אירועים לסיכום:
{events_combined}

אנא צור סיכום יומי מקיף בעברית."""
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": RECAP_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            logger.warning("Empty response from OpenAI")
            return None
        
        import json
        recap_data = json.loads(content)
        
        # Add metadata
        recap_data["source_name"] = source_name
        recap_data["hours"] = hours
        recap_data["generated_at"] = datetime.utcnow().isoformat()
        recap_data["total_events"] = len(events)
        
        logger.info(f"Generated recap for {source_name}: {len(events)} events")
        return recap_data
        
    except Exception as e:
        logger.error(f"Error generating recap for {source_name}: {e}")
        return None


async def test_recap_generator():
    """Test function for development"""
    from app.database import async_session_maker
    
    async with async_session_maker() as db:
        print("\n=== Testing Daily Recap Generator ===\n")
        
        # Get available sources
        sources = await get_available_sources(db)
        print(f"Available sources: {sources}\n")
        
        if sources:
            # Generate recap for first source
            source = sources[0]
            print(f"Generating recap for: {source['source_name']} ({source['event_count']} events)")
            
            recap = await generate_daily_recap(db, source['source_name'])
            if recap:
                print(f"\n✅ Recap generated successfully!")
                print(f"Title: {recap.get('title')}")
                print(f"Summary: {recap.get('executive_summary')[:100]}...")
            else:
                print("❌ Failed to generate recap")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_recap_generator())


"""
Events API Router
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import NewsEvent
from app.schemas import NewsEventResponse, NewsEventsListResponse, StatsResponse

router = APIRouter()


@router.get("/events", response_model=NewsEventsListResponse)
async def get_events(
    hours: int = Query(default=24, ge=1, le=168, description="Filter events from last N hours"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum number of events"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get news events from the database
    
    - **hours**: Filter events detected within last N hours (default: 24)
    - **category**: Optional category filter (military, political, casualties, infrastructure, general)
    - **source**: Optional source filter
    - **limit**: Maximum events to return (default: 100)
    - **offset**: Pagination offset
    """
    # Calculate time threshold
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # Build query
    query = select(NewsEvent).where(NewsEvent.timestamp_detected >= time_threshold)
    
    if category:
        query = query.where(NewsEvent.category == category.lower())
    
    if source:
        query = query.where(NewsEvent.source_name.ilike(f"%{source}%"))
    
    # Get total count
    count_query = select(func.count(NewsEvent.id)).where(NewsEvent.timestamp_detected >= time_threshold)
    if category:
        count_query = count_query.where(NewsEvent.category == category.lower())
    if source:
        count_query = count_query.where(NewsEvent.source_name.ilike(f"%{source}%"))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Execute query with ordering and pagination
    query = query.order_by(desc(NewsEvent.timestamp_detected)).offset(offset).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    
    return NewsEventsListResponse(
        events=[NewsEventResponse.model_validate(e) for e in events],
        total=total,
        filtered_hours=hours
    )


@router.get("/events/{event_id}", response_model=NewsEventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific event by ID"""
    query = select(NewsEvent).where(NewsEvent.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return NewsEventResponse.model_validate(event)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get statistics about news events"""
    # Total events
    total_query = select(func.count(NewsEvent.id))
    total_result = await db.execute(total_query)
    total_events = total_result.scalar() or 0
    
    # Events in last 24 hours
    time_24h = datetime.utcnow() - timedelta(hours=24)
    last_24h_query = select(func.count(NewsEvent.id)).where(NewsEvent.timestamp_detected >= time_24h)
    last_24h_result = await db.execute(last_24h_query)
    events_last_24h = last_24h_result.scalar() or 0
    
    # Events by category
    category_query = select(
        NewsEvent.category, 
        func.count(NewsEvent.id)
    ).group_by(NewsEvent.category)
    category_result = await db.execute(category_query)
    events_by_category = {row[0]: row[1] for row in category_result.all()}
    
    # Events by source
    source_query = select(
        NewsEvent.source_name, 
        func.count(NewsEvent.id)
    ).group_by(NewsEvent.source_name)
    source_result = await db.execute(source_query)
    events_by_source = {row[0]: row[1] for row in source_result.all()}
    
    # Last update time
    last_update_query = select(NewsEvent.timestamp_detected).order_by(desc(NewsEvent.timestamp_detected)).limit(1)
    last_update_result = await db.execute(last_update_query)
    last_update = last_update_result.scalar_one_or_none()
    
    return StatsResponse(
        total_events=total_events,
        events_last_24h=events_last_24h,
        events_by_category=events_by_category,
        events_by_source=events_by_source,
        last_update=last_update
    )


@router.get("/categories")
async def get_categories():
    """Get available event categories with their display info"""
    return {
        "categories": [
            {"id": "military", "name": "Military Activity", "color": "#ef4444", "icon": "explosion"},
            {"id": "political", "name": "Political", "color": "#3b82f6", "icon": "landmark"},
            {"id": "casualties", "name": "Casualties", "color": "#dc2626", "icon": "cross"},
            {"id": "infrastructure", "name": "Infrastructure", "color": "#f59e0b", "icon": "building"},
            {"id": "general", "name": "General News", "color": "#6b7280", "icon": "newspaper"},
        ]
    }


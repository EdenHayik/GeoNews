"""
Daily Recap API Router
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.daily_recap import get_available_sources, generate_daily_recap

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/recap/sources")
async def get_recap_sources(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of available sources with event counts for recap generation
    """
    sources = await get_available_sources(db)
    return {
        "sources": sources,
        "total": len(sources)
    }


@router.post("/recap/generate")
async def create_daily_recap(
    source_name: str = Query(..., description="Source name to generate recap for"),
    hours: int = Query(24, ge=1, le=168, description="Time range in hours (1-168)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered daily recap for a specific source
    
    This is an on-demand operation that uses OpenAI to create a comprehensive
    summary of all events from the specified source within the time range.
    """
    logger.info(f"Generating recap for {source_name} (last {hours} hours)")
    
    recap = await generate_daily_recap(db, source_name, hours)
    
    if not recap:
        return {
            "success": False,
            "error": "Failed to generate recap"
        }
    
    return {
        "success": True,
        "recap": recap
    }


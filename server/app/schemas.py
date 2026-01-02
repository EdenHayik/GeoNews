"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class OpenAIProcessedResult(BaseModel):
    """Schema for OpenAI processed news result"""
    title: str = Field(..., description="Headline/title in Hebrew")
    summary: str = Field(..., description="1-2 sentence summary in Hebrew")
    location_name: Optional[str] = Field(None, description="Physical location name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    category: str = Field("general", description="Event category")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")


class NewsEventResponse(BaseModel):
    """Schema for news event API response"""
    id: int
    source_name: str
    original_url: Optional[str] = None
    original_title: Optional[str] = None
    original_text: Optional[str] = None
    summary_text: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: str
    confidence_score: Optional[float] = None
    image_url: Optional[str] = None
    timestamp_detected: datetime
    timestamp_original: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NewsEventsListResponse(BaseModel):
    """Schema for list of news events"""
    events: List[NewsEventResponse]
    total: int
    filtered_hours: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    timestamp: datetime


class StatsResponse(BaseModel):
    """Statistics response"""
    total_events: int
    events_last_24h: int
    events_by_category: dict
    events_by_source: dict
    last_update: Optional[datetime] = None


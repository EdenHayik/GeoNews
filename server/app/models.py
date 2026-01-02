"""
Database models for GeoNews
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from app.database import Base


class NewsEvent(Base):
    """Model for storing processed news events"""
    __tablename__ = "news_events"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source information
    source_name = Column(String(100), nullable=False, index=True)  # e.g., "Abu Ali Express", "Ynet"
    original_url = Column(String(500), nullable=True)
    original_text = Column(Text, nullable=True)  # Store original text for reference
    
    # AI-processed content
    original_title = Column(Text, nullable=True)  # Translated Hebrew title
    summary_text = Column(Text, nullable=False)
    location_name = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    category = Column(String(50), nullable=False, default="general")  # military, political, casualties, infrastructure, general
    confidence_score = Column(Float, nullable=True)
    
    # Media
    image_url = Column(String(500), nullable=True)
    
    # Timestamps
    timestamp_detected = Column(DateTime, default=datetime.utcnow, index=True)
    timestamp_original = Column(DateTime, nullable=True)  # Original message timestamp
    
    # Unique identifier to prevent duplicates
    content_hash = Column(String(64), unique=True, index=True)
    
    __table_args__ = (
        Index('idx_category_timestamp', 'category', 'timestamp_detected'),
        Index('idx_location', 'latitude', 'longitude'),
    )
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "source_name": self.source_name,
            "original_url": self.original_url,
            "original_title": self.original_title,
            "original_text": self.original_text,
            "summary_text": self.summary_text,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "category": self.category,
            "confidence_score": self.confidence_score,
            "image_url": self.image_url,
            "timestamp_detected": self.timestamp_detected.isoformat() if self.timestamp_detected else None,
            "timestamp_original": self.timestamp_original.isoformat() if self.timestamp_original else None,
        }


class ScraperState(Base):
    """Track scraper state for resumability"""
    __tablename__ = "scraper_state"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, nullable=False)
    last_message_id = Column(Integer, nullable=True)  # For Telegram
    last_scraped_url = Column(String(500), nullable=True)  # For websites
    last_run = Column(DateTime, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "source_name": self.source_name,
            "last_message_id": self.last_message_id,
            "last_scraped_url": self.last_scraped_url,
            "last_run": self.last_run.isoformat() if self.last_run else None,
        }


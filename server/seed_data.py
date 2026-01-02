"""
Seed script to populate database with sample data for testing
Run with: python seed_data.py
"""
import asyncio
import hashlib
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
import sys
sys.path.insert(0, '.')

from app.database import init_db, async_session_maker
from app.models import NewsEvent


# Sample events for testing
SAMPLE_EVENTS = [
    {
        "source_name": "Abu Ali Express",
        "summary_text": "IDF reports successful drone interception over northern Gaza strip. Air defense systems activated in response to aerial threat.",
        "location_name": "Northern Gaza Strip",
        "latitude": 31.55,
        "longitude": 34.50,
        "category": "military",
        "confidence_score": 0.95,
        "hours_ago": 0.5,
    },
    {
        "source_name": "Ynet",
        "summary_text": "Rocket sirens activated in Sderot and surrounding communities. Residents instructed to seek shelter.",
        "location_name": "Sderot",
        "latitude": 31.52,
        "longitude": 34.60,
        "category": "military",
        "confidence_score": 0.92,
        "hours_ago": 1,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Reports of casualties following strike in Khan Yunis area. Emergency services responding to scene.",
        "location_name": "Khan Yunis",
        "latitude": 31.35,
        "longitude": 34.30,
        "category": "casualties",
        "confidence_score": 0.88,
        "hours_ago": 2,
    },
    {
        "source_name": "Ynet",
        "summary_text": "Israeli Cabinet convenes for emergency security meeting in Jerusalem regarding ongoing situation.",
        "location_name": "Jerusalem",
        "latitude": 31.77,
        "longitude": 35.21,
        "category": "political",
        "confidence_score": 0.97,
        "hours_ago": 3,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Infrastructure damage reported following overnight incidents in Ashkelon. Power restoration underway.",
        "location_name": "Ashkelon",
        "latitude": 31.67,
        "longitude": 34.57,
        "category": "infrastructure",
        "confidence_score": 0.85,
        "hours_ago": 4,
    },
    {
        "source_name": "Ynet",
        "summary_text": "Tel Aviv municipality issues statement on emergency preparedness measures for residents.",
        "location_name": "Tel Aviv",
        "latitude": 32.08,
        "longitude": 34.78,
        "category": "general",
        "confidence_score": 0.90,
        "hours_ago": 5,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "IDF ground forces operating in central Gaza. Military spokesperson confirms tactical objectives achieved.",
        "location_name": "Gaza City",
        "latitude": 31.50,
        "longitude": 34.47,
        "category": "military",
        "confidence_score": 0.93,
        "hours_ago": 6,
    },
    {
        "source_name": "Ynet",
        "summary_text": "UNRWA reports on humanitarian situation in southern Gaza. Aid deliveries continue through approved crossings.",
        "location_name": "Rafah",
        "latitude": 31.30,
        "longitude": 34.25,
        "category": "general",
        "confidence_score": 0.89,
        "hours_ago": 7,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Lebanese border area under heightened alert. Hezbollah positions monitored by IDF Northern Command.",
        "location_name": "South Lebanon",
        "latitude": 33.27,
        "longitude": 35.20,
        "category": "military",
        "confidence_score": 0.86,
        "hours_ago": 8,
    },
    {
        "source_name": "Ynet",
        "summary_text": "Diplomatic efforts continue as international envoys arrive in region for talks with Israeli officials.",
        "location_name": "Jerusalem",
        "latitude": 31.77,
        "longitude": 35.21,
        "category": "political",
        "confidence_score": 0.94,
        "hours_ago": 9,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Multiple interceptions reported over Haifa bay area. Iron Dome system successfully engaged threats.",
        "location_name": "Haifa",
        "latitude": 32.79,
        "longitude": 34.99,
        "category": "military",
        "confidence_score": 0.91,
        "hours_ago": 10,
    },
    {
        "source_name": "Ynet",
        "summary_text": "West Bank security operation underway in Jenin. IDF forces entered refugee camp overnight.",
        "location_name": "Jenin",
        "latitude": 32.46,
        "longitude": 35.30,
        "category": "military",
        "confidence_score": 0.88,
        "hours_ago": 11,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Casualties reported in Be'er Sheva following rocket impact. Magen David Adom responding.",
        "location_name": "Be'er Sheva",
        "latitude": 31.25,
        "longitude": 34.79,
        "category": "casualties",
        "confidence_score": 0.87,
        "hours_ago": 12,
    },
    {
        "source_name": "Ynet",
        "summary_text": "Knesset to vote on emergency measures. Opposition leaders briefed on security developments.",
        "location_name": "Jerusalem",
        "latitude": 31.78,
        "longitude": 35.22,
        "category": "political",
        "confidence_score": 0.96,
        "hours_ago": 14,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Building collapse reported in northern Gaza following airstrike. Search and rescue operations ongoing.",
        "location_name": "Beit Lahia",
        "latitude": 31.55,
        "longitude": 34.52,
        "category": "infrastructure",
        "confidence_score": 0.84,
        "hours_ago": 16,
    },
    {
        "source_name": "Ynet",
        "summary_text": "IDF spokesperson releases statement on overnight operations. Military objectives described as achieved.",
        "location_name": "Tel Aviv",
        "latitude": 32.08,
        "longitude": 34.78,
        "category": "general",
        "confidence_score": 0.92,
        "hours_ago": 18,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Naval activity detected off Gaza coast. Israeli Navy enforcing maritime security zone.",
        "location_name": "Gaza Coast",
        "latitude": 31.45,
        "longitude": 34.38,
        "category": "military",
        "confidence_score": 0.83,
        "hours_ago": 20,
    },
    {
        "source_name": "Ynet",
        "summary_text": "Hospital in Nablus reports influx of injured following security incident in area.",
        "location_name": "Nablus",
        "latitude": 32.22,
        "longitude": 35.26,
        "category": "casualties",
        "confidence_score": 0.86,
        "hours_ago": 22,
    },
    {
        "source_name": "Abu Ali Express",
        "summary_text": "Power outages affecting multiple areas of central Gaza. Infrastructure repairs hampered by conditions.",
        "location_name": "Deir al-Balah",
        "latitude": 31.42,
        "longitude": 34.35,
        "category": "infrastructure",
        "confidence_score": 0.81,
        "hours_ago": 23,
    },
    {
        "source_name": "Ynet",
        "summary_text": "US Secretary of State to arrive for regional consultations. Meetings scheduled with Israeli leadership.",
        "location_name": "Ben Gurion Airport",
        "latitude": 32.01,
        "longitude": 34.89,
        "category": "political",
        "confidence_score": 0.98,
        "hours_ago": 24,
    },
]


def generate_hash(text: str, timestamp: datetime) -> str:
    """Generate unique content hash"""
    content = f"{text[:200]}_{timestamp.isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()


async def seed_database():
    """Seed database with sample events"""
    print("🌱 Seeding database with sample events...")
    
    # Initialize database
    await init_db()
    
    async with async_session_maker() as db:
        for event_data in SAMPLE_EVENTS:
            # Calculate timestamp
            hours_ago = event_data.pop("hours_ago")
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
            
            # Create event
            event = NewsEvent(
                source_name=event_data["source_name"],
                original_url=f"https://example.com/news/{random.randint(1000, 9999)}",
                original_text=event_data["summary_text"],
                summary_text=event_data["summary_text"],
                location_name=event_data["location_name"],
                latitude=event_data["latitude"],
                longitude=event_data["longitude"],
                category=event_data["category"],
                confidence_score=event_data["confidence_score"],
                image_url=None,
                timestamp_detected=timestamp,
                timestamp_original=timestamp - timedelta(minutes=random.randint(5, 30)),
                content_hash=generate_hash(event_data["summary_text"], timestamp),
            )
            
            db.add(event)
        
        await db.commit()
        print(f"✅ Seeded {len(SAMPLE_EVENTS)} events successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())


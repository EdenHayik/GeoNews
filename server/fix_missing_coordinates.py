#!/usr/bin/env python3
"""
Fix missing coordinates for existing events
"""
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy import select
from app.database import async_session_maker
from app.models import NewsEvent

# Tehran coordinates for Iran events
IRAN_COORDS = (35.69, 51.42)

async def fix_coordinates():
    """Fix missing coordinates for Iran and other locations"""
    async with async_session_maker() as db:
        # Find events with location but no coordinates
        query = select(NewsEvent).where(
            NewsEvent.location_name.isnot(None),
            NewsEvent.latitude.is_(None)
        )
        result = await db.execute(query)
        events = result.scalars().all()
        
        print(f"Found {len(events)} events with missing coordinates\n")
        
        fixed_count = 0
        for event in events:
            location = event.location_name.lower()
            
            # Check if it's Iran
            if 'איר' in location or 'iran' in location:
                event.latitude = IRAN_COORDS[0]
                event.longitude = IRAN_COORDS[1]
                print(f"✅ Fixed Iran event (ID {event.id}): {event.location_name}")
                print(f"   Coordinates: {IRAN_COORDS}")
                print(f"   Summary: {event.summary_text[:80]}...")
                print()
                fixed_count += 1
        
        if fixed_count > 0:
            await db.commit()
            print(f"\n🎉 Fixed {fixed_count} events!")
        else:
            print("No Iran events to fix.")

if __name__ == '__main__':
    asyncio.run(fix_coordinates())


"""
AI Processing Service using OpenAI API
Processes raw news text to extract locations, summaries, and categories
"""
import json
import logging
from typing import Optional
from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import OpenAIProcessedResult

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Fallback coordinates for common locations (when AI fails to provide them)
# This is a safety net - the AI should provide coordinates, but this ensures we never have null
LOCATION_FALLBACKS = {
    # Middle East
    "איראן": (35.69, 51.42), "אירן": (35.69, 51.42), "iran": (35.69, 51.42),
    "טהראן": (35.69, 51.42), "tehran": (35.69, 51.42),
    "ישראל": (31.77, 35.21), "israel": (31.77, 35.21),
    "תל אביב": (32.08, 34.78), "tel aviv": (32.08, 34.78),
    "ירושלים": (31.77, 35.21), "jerusalem": (31.77, 35.21),
    "חיפה": (32.79, 34.99), "haifa": (32.79, 34.99),
    "אילת": (29.55, 34.95), "eilat": (29.55, 34.95),
    "אשקלון": (31.67, 34.57), "ashkelon": (31.67, 34.57),
    "עזה": (31.50, 34.47), "gaza": (31.50, 34.47),
    "רצועת עזה": (31.50, 34.47), "gaza strip": (31.50, 34.47),
    "לבנון": (33.89, 35.50), "lebanon": (33.89, 35.50),
    "ביירות": (33.89, 35.50), "beirut": (33.89, 35.50),
    "סוריה": (33.51, 36.29), "syria": (33.51, 36.29),
    "דמשק": (33.51, 36.29), "damascus": (33.51, 36.29),
    "עיראק": (33.31, 44.36), "iraq": (33.31, 44.36),
    "בגדד": (33.31, 44.36), "baghdad": (33.31, 44.36),
    "מצרים": (30.04, 31.24), "egypt": (30.04, 31.24),
    "קהיר": (30.04, 31.24), "cairo": (30.04, 31.24),
    "ירדן": (31.95, 35.93), "jordan": (31.95, 35.93),
    "עמאן": (31.95, 35.93), "amman": (31.95, 35.93),
    "סעודיה": (24.71, 46.67), "saudi arabia": (24.71, 46.67),
    "ריאד": (24.71, 46.67), "riyadh": (24.71, 46.67),
    "תימן": (15.55, 48.52), "yemen": (15.55, 48.52),
    
    # Europe
    "בריטניה": (51.51, -0.13), "uk": (51.51, -0.13), "united kingdom": (51.51, -0.13),
    "לונדון": (51.51, -0.13), "london": (51.51, -0.13),
    "צרפת": (48.86, 2.35), "france": (48.86, 2.35),
    "פריז": (48.86, 2.35), "paris": (48.86, 2.35),
    "גרמניה": (52.52, 13.41), "germany": (52.52, 13.41),
    "ברלין": (52.52, 13.41), "berlin": (52.52, 13.41),
    "איטליה": (41.90, 12.50), "italy": (41.90, 12.50),
    "רומא": (41.90, 12.50), "rome": (41.90, 12.50),
    "ספרד": (40.42, -3.70), "spain": (40.42, -3.70),
    "מדריד": (40.42, -3.70), "madrid": (40.42, -3.70),
    "רוסיה": (55.75, 37.62), "russia": (55.75, 37.62),
    "מוסקבה": (55.75, 37.62), "moscow": (55.75, 37.62),
    "הולנד": (52.37, 4.90), "netherlands": (52.37, 4.90),
    "אמסטרדם": (52.37, 4.90), "amsterdam": (52.37, 4.90),
    "שוויץ": (46.95, 7.45), "switzerland": (46.95, 7.45),
    
    # Americas
    "ארהב": (38.91, -77.04), "usa": (38.91, -77.04), "united states": (38.91, -77.04),
    "ניו יורק": (40.71, -74.01), "new york": (40.71, -74.01),
    "וושינגטון": (38.91, -77.04), "washington": (38.91, -77.04),
    "לוס אנג'לס": (34.05, -118.24), "los angeles": (34.05, -118.24),
    "מקסיקו": (19.43, -99.13), "mexico": (19.43, -99.13),
    "ברזיל": (-15.79, -47.89), "brazil": (-15.79, -47.89),
    "ארגנטינה": (-34.60, -58.38), "argentina": (-34.60, -58.38),
    
    # Asia
    "סין": (39.90, 116.40), "china": (39.90, 116.40),
    "בייג'ינג": (39.90, 116.40), "beijing": (39.90, 116.40),
    "יפן": (35.68, 139.65), "japan": (35.68, 139.65),
    "טוקיו": (35.68, 139.65), "tokyo": (35.68, 139.65),
    "הודו": (28.61, 77.21), "india": (28.61, 77.21),
    "דלהי": (28.61, 77.21), "delhi": (28.61, 77.21),
    "קוריאה": (37.57, 126.98), "korea": (37.57, 126.98), "south korea": (37.57, 126.98),
    "סיאול": (37.57, 126.98), "seoul": (37.57, 126.98),
    "תאילנד": (13.76, 100.50), "thailand": (13.76, 100.50),
    "בנגקוק": (13.76, 100.50), "bangkok": (13.76, 100.50),
    "סינגפור": (1.35, 103.82), "singapore": (1.35, 103.82),
    "פקיסטן": (33.72, 73.06), "pakistan": (33.72, 73.06),
    "אפגניסטן": (34.53, 69.17), "afghanistan": (34.53, 69.17),
    
    # Africa
    "דרום אפריקה": (-26.20, 28.05), "south africa": (-26.20, 28.05),
    "ניגריה": (6.52, 3.38), "nigeria": (6.52, 3.38),
    "קניה": (-1.29, 36.82), "kenya": (-1.29, 36.82),
    "אתיופיה": (9.02, 38.75), "ethiopia": (9.02, 38.75),
    
    # Oceania
    "אוסטרליה": (-33.87, 151.21), "australia": (-33.87, 151.21),
    "סידני": (-33.87, 151.21), "sydney": (-33.87, 151.21),
    "ניו זילנד": (-36.85, 174.76), "new zealand": (-36.85, 174.76),
}


def apply_location_fallback(location_name: Optional[str], latitude: Optional[float], longitude: Optional[float]) -> tuple[Optional[float], Optional[float]]:
    """
    Apply fallback coordinates if location name exists but coordinates are missing.
    Returns (latitude, longitude) tuple.
    """
    if not location_name or (latitude is not None and longitude is not None):
        return (latitude, longitude)
    
    # Normalize location name for matching
    normalized = location_name.strip().lower()
    
    # Check direct match
    if normalized in LOCATION_FALLBACKS:
        coords = LOCATION_FALLBACKS[normalized]
        logger.info(f"Applied fallback coordinates for '{location_name}': {coords}")
        return coords
    
    # Check if any fallback location is contained in the name
    for fallback_location, coords in LOCATION_FALLBACKS.items():
        if fallback_location in normalized or normalized in fallback_location:
            logger.info(f"Applied fallback coordinates for '{location_name}' (matched '{fallback_location}'): {coords}")
            return coords
    
    logger.warning(f"No fallback coordinates found for location: '{location_name}'")
    return (latitude, longitude)

# System prompt for news processing
SYSTEM_PROMPT = """You are an expert intelligence analyst specializing in global geopolitical events. Your task is to analyze news text (in Hebrew, Arabic, or English) and extract structured information.

For each piece of text, you must:
1. **Extract Title in HEBREW**: Extract or create a concise headline/title in HEBREW (עברית). If the original has a title or headline, translate it to Hebrew. If not, create a short title (5-10 words) that captures the main point in Hebrew.
2. **Geolocate**: Identify the most specific physical location mentioned. Convert this location name into latitude/longitude coordinates.
3. **Summarize in HEBREW**: Create a concise, factual 1-2 sentence summary in **HEBREW** (עברית). Be neutral and objective. This should provide additional context beyond the title.
4. **Categorize**: Classify into one of these categories:
   - "military" - Military operations, strikes, interceptions, drone activity
   - "political" - Political statements, diplomatic events, government actions
   - "casualties" - Reports of injuries, deaths, humanitarian incidents
   - "infrastructure" - Damage to buildings, roads, utilities, civilian structures
   - "general" - Other news that doesn't fit above categories

⚠️ CRITICAL GEOLOCATION RULES - READ CAREFULLY:
1. **NEVER return null for latitude/longitude if a location name is provided**
2. **ALWAYS provide approximate coordinates even if you're not 100% certain**
3. **For cities**: Use the city center coordinates
4. **For countries**: Use the capital city or geographic center
5. **For regions**: Use a central point in that region
6. **For vague locations**: Make your best educated estimate based on context
7. **ONLY use null coordinates if NO location is mentioned at all**

EXAMPLE COORDINATE GUIDELINES (but not limited to these):
- Middle East: Gaza (31.50, 34.47), Jerusalem (31.77, 35.21), Tel Aviv (32.08, 34.78), Beirut (33.89, 35.50), Damascus (33.51, 36.29), Tehran (35.69, 51.42), Baghdad (33.31, 44.36), Amman (31.95, 35.93), Cairo (30.04, 31.24), Riyadh (24.71, 46.67)
- Europe: London (51.51, -0.13), Paris (48.86, 2.35), Berlin (52.52, 13.41), Rome (41.90, 12.50), Madrid (40.42, -3.70), Moscow (55.75, 37.62), Amsterdam (52.37, 4.90), Brussels (50.85, 4.35)
- Americas: New York (40.71, -74.01), Washington DC (38.91, -77.04), Los Angeles (34.05, -118.24), Mexico City (19.43, -99.13), Brasília (−15.79, -47.89), Buenos Aires (-34.60, -58.38)
- Asia: Beijing (39.90, 116.40), Tokyo (35.68, 139.65), Delhi (28.61, 77.21), Mumbai (19.08, 72.88), Seoul (37.57, 126.98), Bangkok (13.76, 100.50), Singapore (1.35, 103.82)
- Africa: Johannesburg (-26.20, 28.05), Lagos (6.52, 3.38), Nairobi (-1.29, 36.82), Addis Ababa (9.02, 38.75)
- Oceania: Sydney (-33.87, 151.21), Melbourne (-37.81, 144.96), Auckland (-36.85, 174.76)

IF YOU DON'T KNOW EXACT COORDINATES:
- Google the location mentally and estimate
- Use country center if city is unknown
- Use regional approximation if specific area is unclear
- NEVER give up and return null - always provide something

CRITICAL: Both "title" and "summary" fields MUST be in Hebrew (עברית).
CRITICAL: If you provide a "location_name", you MUST also provide "latitude" and "longitude" - NEVER EVER use null.

You must respond ONLY with a valid JSON object, no other text. Example:
{
  "title": "צה״ל מיירט רחפן מעל צפון עזה",
  "summary": "כוחות צה״ל דיווחו על זיהוי ויירוט מזל״ט עוין שחדר מצפון רצועת עזה. לא דווח על נפגעים.",
  "location_name": "צפון רצועת עזה",
  "latitude": 31.55,
  "longitude": 34.50,
  "category": "military",
  "confidence_score": 0.95
}"""


async def process_news_text(text: str, source_hint: str = "") -> Optional[OpenAIProcessedResult]:
    """
    Process raw news text using OpenAI to extract structured information.
    
    Args:
        text: Raw news text (Hebrew, Arabic, or English)
        source_hint: Optional hint about the source for context
        
    Returns:
        OpenAIProcessedResult with extracted information, or None if processing fails
    """
    if not client:
        logger.warning("OpenAI client not configured - skipping AI processing")
        return None
    
    if not text or len(text.strip()) < 10:
        logger.debug("Text too short for processing")
        return None
    
    try:
        # Prepare user message with context
        user_message = f"Source: {source_hint}\n\nText to analyze:\n{text}" if source_hint else text
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content
        if not content:
            logger.warning("Empty response from OpenAI")
            return None
        
        # Parse JSON response
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            logger.debug(f"Raw response: {content}")
            return None
        
        # Validate and create result
        result = OpenAIProcessedResult(
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            location_name=data.get("location_name"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            category=data.get("category", "general").lower(),
            confidence_score=data.get("confidence_score")
        )
        
        # Apply fallback coordinates if needed
        if result.location_name and (result.latitude is None or result.longitude is None):
            result.latitude, result.longitude = apply_location_fallback(
                result.location_name, 
                result.latitude, 
                result.longitude
            )
        
        # Validate category
        valid_categories = ["military", "political", "casualties", "infrastructure", "general"]
        if result.category not in valid_categories:
            result.category = "general"
        
        logger.debug(f"Processed text: {result.title} | {result.summary[:50]}... -> {result.location_name} ({result.latitude}, {result.longitude})")
        return result
        
    except Exception as e:
        logger.error(f"Error processing text with OpenAI: {e}")
        return None


async def batch_process_texts(texts: list[tuple[str, str]]) -> list[Optional[OpenAIProcessedResult]]:
    """
    Process multiple texts in parallel.
    
    Args:
        texts: List of (text, source_hint) tuples
        
    Returns:
        List of processing results
    """
    import asyncio
    
    tasks = [process_news_text(text, hint) for text, hint in texts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Batch processing error: {result}")
            processed.append(None)
        else:
            processed.append(result)
    
    return processed


# Test function for development
async def test_processor():
    """Test the AI processor with sample text"""
    test_texts = [
        ("תקיפה אווירית בצפון רצועת עזה. צה\"ל דיווח על יירוט מזל\"ט", "Test"),
        ("רקטות נורו לעבר אשקלון, אין נפגעים", "Test"),
        ("The IDF conducted operations in Jenin refugee camp overnight", "Test"),
    ]
    
    for text, source in test_texts:
        print(f"\nProcessing: {text[:50]}...")
        result = await process_news_text(text, source)
        if result:
            print(f"  Summary: {result.summary}")
            print(f"  Location: {result.location_name} ({result.latitude}, {result.longitude})")
            print(f"  Category: {result.category}")
        else:
            print("  Failed to process")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_processor())


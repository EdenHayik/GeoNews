"""
GeoNews FastAPI Application
Real-time news aggregation and geospatial visualization
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import events, recap
from app.services.scheduler import start_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting GeoNews server...")
    await init_db()
    logger.info("✅ Database initialized")
    
    # Start background scrapers
    await start_scheduler()
    logger.info("✅ Scheduler started")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down GeoNews server...")
    await stop_scheduler()
    await close_db()
    logger.info("✅ Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="GeoNews API",
    description="Real-time news aggregation and geospatial visualization API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router, prefix="/api", tags=["events"])
app.include_router(recap.router, prefix="/api", tags=["recap"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": "GeoNews API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    from app.services.db_cleanup import get_database_stats
    
    db_stats = await get_database_stats()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "stats": db_stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


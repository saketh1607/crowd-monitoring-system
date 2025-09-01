"""
FastAPI main application for Emergency Management System
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from datetime import datetime

from config.settings import settings
from src.data.database import get_db, init_db
from src.data.models import (
    EventCreate, EventResponse, EventUpdate,
    EmergencyCreate, EmergencyResponse, EmergencyUpdate,
    SensorCreate, SensorReading, ResourceCreate, ResourceResponse
)
from src.api.routes import events, sensors, resources, monitoring
from src.api.routes import emergencies_simple as emergencies
# from src.api.websocket import websocket_manager  # Temporarily disabled

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Emergency Management System for Large Events",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events.router, prefix=f"{settings.API_PREFIX}/events", tags=["events"])
app.include_router(emergencies.router, prefix=f"{settings.API_PREFIX}/emergencies", tags=["emergencies"])
app.include_router(sensors.router, prefix=f"{settings.API_PREFIX}/sensors", tags=["sensors"])
app.include_router(resources.router, prefix=f"{settings.API_PREFIX}/resources", tags=["resources"])
app.include_router(monitoring.router, prefix=f"{settings.API_PREFIX}/monitoring", tags=["monitoring"])

# Include WebSocket
# app.include_router(websocket_manager.router)  # Temporarily disabled


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Emergency Management System")
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Emergency Management System")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Emergency Management System API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

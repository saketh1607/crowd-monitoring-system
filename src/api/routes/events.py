"""
Event management API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from src.data.database import get_db
from src.data.models import Event, EventCreate, EventResponse, EventUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=EventResponse)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    try:
        db_event = Event(**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        logger.info(f"Event created: {db_event.id}")
        return db_event
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[EventResponse])
async def get_events(
    venue: Optional[str] = None,
    risk_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of events with optional filters"""
    try:
        query = db.query(Event)
        
        if venue:
            query = query.filter(Event.venue.contains(venue))
        if risk_level:
            query = query.filter(Event.risk_level == risk_level)
        
        events = query.offset(skip).limit(limit).all()
        return events
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get specific event by ID"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db)
):
    """Update event details"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Update fields
        update_data = event_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        db.commit()
        db.refresh(event)
        
        logger.info(f"Event updated: {event_id}")
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        db.delete(event)
        db.commit()
        
        logger.info(f"Event deleted: {event_id}")
        return {"message": "Event deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

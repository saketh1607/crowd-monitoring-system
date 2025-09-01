"""
Emergency management API routes
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.data.database import get_db
from src.data.models import Emergency, EmergencyCreate, EmergencyResponse, EmergencyUpdate
from src.models.emergency_detector import FireDetectionModel, CrowdDensityAnalyzer, BehaviorAnalyzer
from src.models.response_optimizer import ResourceAllocator, EvacuationPlanner, CommunicationCoordinator
from src.api.websocket import websocket_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize ML models
fire_detector = FireDetectionModel()
crowd_analyzer = CrowdDensityAnalyzer()
behavior_analyzer = BehaviorAnalyzer()
resource_allocator = ResourceAllocator()
communication_coordinator = CommunicationCoordinator()


@router.post("/", response_model=EmergencyResponse)
async def create_emergency(
    emergency: EmergencyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new emergency incident"""
    try:
        # Create emergency record
        db_emergency = Emergency(**emergency.dict())
        db.add(db_emergency)
        db.commit()
        db.refresh(db_emergency)
        
        # Trigger emergency response workflow
        background_tasks.add_task(
            handle_emergency_response,
            db_emergency.id,
            emergency.dict()
        )
        
        # Send real-time notification
        await websocket_manager.broadcast({
            "type": "emergency_created",
            "data": {
                "id": db_emergency.id,
                "type": db_emergency.type,
                "severity": db_emergency.severity,
                "location": {
                    "x": db_emergency.location_x,
                    "y": db_emergency.location_y
                },
                "timestamp": db_emergency.detected_at.isoformat()
            }
        })
        
        logger.info(f"Emergency created: {db_emergency.id}")
        return db_emergency
        
    except Exception as e:
        logger.error(f"Error creating emergency: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[EmergencyResponse])
async def get_emergencies(
    event_id: Optional[int] = None,
    status: Optional[str] = None,
    emergency_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of emergencies with optional filters"""
    try:
        query = db.query(Emergency)
        
        if event_id:
            query = query.filter(Emergency.event_id == event_id)
        if status:
            query = query.filter(Emergency.status == status)
        if emergency_type:
            query = query.filter(Emergency.type == emergency_type)
        
        emergencies = query.offset(skip).limit(limit).all()
        return emergencies
        
    except Exception as e:
        logger.error(f"Error fetching emergencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{emergency_id}", response_model=EmergencyResponse)
async def get_emergency(emergency_id: int, db: Session = Depends(get_db)):
    """Get specific emergency by ID"""
    try:
        emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency not found")
        return emergency
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching emergency {emergency_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{emergency_id}", response_model=EmergencyResponse)
async def update_emergency(
    emergency_id: int,
    emergency_update: EmergencyUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update emergency status and details"""
    try:
        emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency not found")
        
        # Update fields
        update_data = emergency_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(emergency, field, value)
        
        emergency.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(emergency)
        
        # Send real-time update
        await websocket_manager.broadcast({
            "type": "emergency_updated",
            "data": {
                "id": emergency.id,
                "status": emergency.status,
                "severity": emergency.severity,
                "timestamp": emergency.updated_at.isoformat()
            }
        })
        
        logger.info(f"Emergency updated: {emergency_id}")
        return emergency
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating emergency {emergency_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect/fire")
async def detect_fire(image_data: Dict[str, Any]):
    """Detect fire in uploaded image"""
    try:
        # This would typically receive base64 encoded image
        # For demo purposes, we'll simulate detection
        result = {
            "fire_detected": False,
            "confidence": 0.3,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In real implementation:
        # import base64, cv2, numpy as np
        # image_bytes = base64.b64decode(image_data["image"])
        # image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        # result = fire_detector.detect_fire(image)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in fire detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/crowd")
async def analyze_crowd(image_data: Dict[str, Any]):
    """Analyze crowd density from image"""
    try:
        # Simulate crowd analysis
        result = {
            "people_count": 45,
            "density_per_sqm": 2.3,
            "density_level": "medium",
            "area_sqm": 100.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In real implementation:
        # result = crowd_analyzer.calculate_density(image, area_sqm)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in crowd analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/behavior")
async def analyze_behavior(sensor_data: Dict[str, Any]):
    """Analyze behavior for security threats"""
    try:
        # Simulate behavior analysis
        result = {
            "threat_detected": False,
            "confidence": 0.2,
            "behavior_type": "normal",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # In real implementation:
        # motion_data = np.array(sensor_data.get("motion", []))
        # audio_data = np.array(sensor_data.get("audio", []))
        # result = behavior_analyzer.analyze_behavior(motion_data, audio_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in behavior analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{emergency_id}/response")
async def optimize_response(emergency_id: int, db: Session = Depends(get_db)):
    """Optimize emergency response and resource allocation"""
    try:
        emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency not found")
        
        # Get optimal resource assignments
        assignments = resource_allocator.optimize_assignments()
        recommendations = resource_allocator.get_assignment_recommendations()
        
        # Create communication plan
        from src.models.response_optimizer import EmergencyIncident
        incident = EmergencyIncident(
            id=str(emergency.id),
            type=emergency.type,
            location=(emergency.location_x or 0, emergency.location_y or 0),
            severity=emergency.severity,
            priority=1,
            detected_at=emergency.detected_at,
            estimated_response_time=300,
            required_resources=["medical_personnel"] if emergency.type == "medical" else ["fire_personnel"]
        )
        
        communication_plan = communication_coordinator.create_communication_plan(incident, assignments)
        
        return {
            "emergency_id": emergency_id,
            "resource_assignments": assignments,
            "recommendations": recommendations,
            "communication_plan": communication_plan,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing response for emergency {emergency_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{emergency_id}/evacuation")
async def plan_evacuation(
    emergency_id: int,
    venue_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Plan evacuation for emergency"""
    try:
        emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency not found")
        
        # Create evacuation planner
        evacuation_planner = EvacuationPlanner(venue_data)
        
        # Plan evacuation
        incident_location = (emergency.location_x or 0, emergency.location_y or 0)
        crowd_distribution = venue_data.get("crowd_distribution", {})
        
        evacuation_plan = evacuation_planner.calculate_evacuation_plan(
            incident_location, crowd_distribution
        )
        
        return {
            "emergency_id": emergency_id,
            "evacuation_plan": evacuation_plan,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error planning evacuation for emergency {emergency_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_emergency_response(emergency_id: int, emergency_data: Dict[str, Any]):
    """Background task to handle emergency response workflow"""
    try:
        logger.info(f"Processing emergency response for {emergency_id}")
        
        # Add incident to resource allocator
        from src.models.response_optimizer import EmergencyIncident
        incident = EmergencyIncident(
            id=str(emergency_id),
            type=emergency_data["type"],
            location=(emergency_data.get("location_x", 0), emergency_data.get("location_y", 0)),
            severity=emergency_data.get("severity", "medium"),
            priority=1,
            detected_at=datetime.utcnow(),
            estimated_response_time=300,
            required_resources=[]
        )
        
        resource_allocator.add_incident(incident)
        
        # Optimize assignments
        assignments = resource_allocator.optimize_assignments()
        
        # Send notifications
        await websocket_manager.broadcast({
            "type": "response_optimized",
            "data": {
                "emergency_id": emergency_id,
                "assignments": assignments,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        logger.info(f"Emergency response processed for {emergency_id}")
        
    except Exception as e:
        logger.error(f"Error in emergency response workflow: {e}")

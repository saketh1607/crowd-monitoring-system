"""
Simplified emergency management API routes (without ML model loading at startup)
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import numpy as np

from src.data.database import get_db
from src.data.models import Emergency, EmergencyCreate, EmergencyResponse, EmergencyUpdate

logger = logging.getLogger(__name__)
router = APIRouter()

# Global ML model instances (loaded on first use)
_fire_detector = None
_crowd_analyzer = None
_behavior_analyzer = None


def get_fire_detector():
    """Get fire detector instance (lazy loading)"""
    global _fire_detector
    if _fire_detector is None:
        try:
            from src.models.emergency_detector import FireDetectionModel
            _fire_detector = FireDetectionModel(model_path="data/models/fire_detection_model.h5")
            logger.info("Fire detector loaded")
        except Exception as e:
            logger.error(f"Error loading fire detector: {e}")
            _fire_detector = None
    return _fire_detector


def get_crowd_analyzer():
    """Get crowd analyzer instance (lazy loading)"""
    global _crowd_analyzer
    if _crowd_analyzer is None:
        try:
            from src.models.emergency_detector import CrowdDensityAnalyzer
            _crowd_analyzer = CrowdDensityAnalyzer()
            logger.info("Crowd analyzer loaded")
        except Exception as e:
            logger.error(f"Error loading crowd analyzer: {e}")
            _crowd_analyzer = None
    return _crowd_analyzer


def get_behavior_analyzer():
    """Get behavior analyzer instance (lazy loading)"""
    global _behavior_analyzer
    if _behavior_analyzer is None:
        try:
            from src.models.emergency_detector import BehaviorAnalyzer
            _behavior_analyzer = BehaviorAnalyzer()
            logger.info("Behavior analyzer loaded")
        except Exception as e:
            logger.error(f"Error loading behavior analyzer: {e}")
            _behavior_analyzer = None
    return _behavior_analyzer


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


@router.post("/detect/fire")
async def detect_fire(image_data: Dict[str, Any]):
    """Detect fire in uploaded image"""
    try:
        fire_detector = get_fire_detector()
        
        if fire_detector is None:
            # Fallback to mock detection
            return {
                "fire_detected": False,
                "confidence": 0.3,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Using mock detection (model not available)"
            }
        
        # In a real implementation, you would decode the base64 image
        # For now, simulate detection with mock data
        mock_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        result = fire_detector.detect_fire(mock_image)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in fire detection: {e}")
        return {
            "fire_detected": False,
            "confidence": 0.0,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/analyze/crowd")
async def analyze_crowd(image_data: Dict[str, Any]):
    """Analyze crowd density from image"""
    try:
        crowd_analyzer = get_crowd_analyzer()
        
        if crowd_analyzer is None:
            # Fallback to mock analysis
            return {
                "people_count": 45,
                "density_per_sqm": 2.3,
                "density_level": "medium",
                "area_sqm": image_data.get("area_sqm", 100.0),
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Using mock analysis (model not available)"
            }
        
        # Simulate crowd analysis
        area_sqm = image_data.get("area_sqm", 100.0)
        mock_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        result = crowd_analyzer.calculate_density(mock_image, area_sqm)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in crowd analysis: {e}")
        return {
            "people_count": 0,
            "density_per_sqm": 0.0,
            "density_level": "unknown",
            "area_sqm": image_data.get("area_sqm", 100.0),
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/analyze/behavior")
async def analyze_behavior(sensor_data: Dict[str, Any]):
    """Analyze behavior for security threats"""
    try:
        behavior_analyzer = get_behavior_analyzer()
        
        if behavior_analyzer is None:
            # Fallback to mock analysis
            return {
                "threat_detected": False,
                "confidence": 0.2,
                "behavior_type": "normal",
                "timestamp": datetime.utcnow().isoformat(),
                "note": "Using mock analysis (model not available)"
            }
        
        # Extract sensor data
        motion_data = np.array(sensor_data.get("motion_data", [1, 2, 3, 4, 5]))
        audio_data = np.array(sensor_data.get("audio_data", [60, 65, 70, 75, 80]))
        
        result = behavior_analyzer.analyze_behavior(motion_data, audio_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in behavior analysis: {e}")
        return {
            "threat_detected": False,
            "confidence": 0.0,
            "behavior_type": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/{emergency_id}/response")
async def optimize_response(emergency_id: int, db: Session = Depends(get_db)):
    """Optimize emergency response and resource allocation"""
    try:
        emergency = db.query(Emergency).filter(Emergency.id == emergency_id).first()
        if not emergency:
            raise HTTPException(status_code=404, detail="Emergency not found")
        
        # Mock response optimization
        assignments = {
            "AMBULANCE_1": f"EMERGENCY_{emergency_id}",
            "MEDICAL_TEAM_A": f"EMERGENCY_{emergency_id}"
        }
        
        recommendations = [
            {
                "resource_id": "AMBULANCE_1",
                "estimated_response_time": 180,
                "priority": 1,
                "action": "Dispatch immediately"
            }
        ]
        
        communication_plan = {
            "notifications": [
                {
                    "audience": "emergency_services",
                    "message": f"{emergency.type} emergency at location ({emergency.location_x}, {emergency.location_y})",
                    "method": "direct_call",
                    "priority": 1
                }
            ]
        }
        
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

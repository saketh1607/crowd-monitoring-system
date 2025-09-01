"""
Monitoring and dashboard API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from datetime import datetime

from src.data.database import get_db
from src.data.models import Event, Emergency, Resource

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard overview data"""
    try:
        # Count active emergencies
        active_emergencies = db.query(Emergency).filter(
            Emergency.status.in_(["detected", "confirmed", "responding"])
        ).count()
        
        # Count total events
        total_events = db.query(Event).count()
        
        # Count available resources
        available_resources = db.query(Resource).filter(Resource.is_available == True).count()
        
        # Calculate overall risk level (simplified)
        critical_emergencies = db.query(Emergency).filter(
            Emergency.severity == "critical",
            Emergency.status.in_(["detected", "confirmed", "responding"])
        ).count()
        
        if critical_emergencies > 0:
            risk_level = "critical"
        elif active_emergencies > 5:
            risk_level = "high"
        elif active_emergencies > 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Get recent incidents
        recent_incidents = db.query(Emergency).order_by(
            Emergency.detected_at.desc()
        ).limit(10).all()
        
        return {
            "active_emergencies": active_emergencies,
            "total_events": total_events,
            "available_resources": available_resources,
            "risk_level": risk_level,
            "recent_incidents": [
                {
                    "id": incident.id,
                    "type": incident.type,
                    "severity": incident.severity,
                    "status": incident.status,
                    "detected_at": incident.detected_at.isoformat()
                }
                for incident in recent_incidents
            ],
            "system_status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk/{event_id}")
async def get_risk_assessment(event_id: int, db: Session = Depends(get_db)):
    """Get risk assessment for specific event"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Count emergencies for this event
        emergencies = db.query(Emergency).filter(Emergency.event_id == event_id).all()
        
        # Calculate risk factors
        risk_factors = {
            "total_emergencies": len(emergencies),
            "critical_emergencies": len([e for e in emergencies if e.severity == "critical"]),
            "active_emergencies": len([e for e in emergencies if e.status in ["detected", "confirmed", "responding"]]),
            "attendance_ratio": (event.actual_attendance or event.expected_attendance or 0) / max(event.expected_attendance or 1, 1),
            "weather_risk": calculate_weather_risk(event.weather_conditions or {}),
            "event_risk_level": event.risk_level
        }
        
        # Calculate overall risk score (0-1)
        risk_score = min(1.0, (
            risk_factors["critical_emergencies"] * 0.4 +
            risk_factors["active_emergencies"] * 0.2 +
            min(risk_factors["attendance_ratio"], 1.0) * 0.2 +
            risk_factors["weather_risk"] * 0.2
        ))
        
        return {
            "event_id": event_id,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendations": generate_risk_recommendations(risk_factors),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating risk assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_live_metrics(db: Session = Depends(get_db)):
    """Get live system metrics"""
    try:
        # Emergency metrics
        emergency_metrics = {
            "total": db.query(Emergency).count(),
            "active": db.query(Emergency).filter(
                Emergency.status.in_(["detected", "confirmed", "responding"])
            ).count(),
            "resolved_today": db.query(Emergency).filter(
                Emergency.resolved_at >= datetime.utcnow().date()
            ).count() if db.query(Emergency).filter(Emergency.resolved_at.isnot(None)).first() else 0
        }
        
        # Resource metrics
        resource_metrics = {
            "total": db.query(Resource).count(),
            "available": db.query(Resource).filter(Resource.is_available == True).count(),
            "deployed": db.query(Resource).filter(Resource.is_available == False).count()
        }
        
        # Event metrics
        event_metrics = {
            "total": db.query(Event).count(),
            "active": db.query(Event).filter(
                Event.start_time <= datetime.utcnow(),
                Event.end_time >= datetime.utcnow()
            ).count()
        }
        
        return {
            "emergency_metrics": emergency_metrics,
            "resource_metrics": resource_metrics,
            "event_metrics": event_metrics,
            "system_health": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching live metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_weather_risk(weather_conditions: Dict[str, Any]) -> float:
    """Calculate weather-related risk score (0-1)"""
    risk = 0.0
    
    temp = weather_conditions.get("temperature", 20)
    if temp > 35 or temp < 0:
        risk += 0.4
    elif temp > 30 or temp < 5:
        risk += 0.2
    
    wind_speed = weather_conditions.get("wind_speed", 0)
    if wind_speed > 25:
        risk += 0.3
    elif wind_speed > 15:
        risk += 0.1
    
    precipitation = weather_conditions.get("precipitation", 0)
    if precipitation > 10:
        risk += 0.3
    elif precipitation > 2:
        risk += 0.1
    
    return min(risk, 1.0)


def generate_risk_recommendations(risk_factors: Dict[str, Any]) -> list:
    """Generate risk mitigation recommendations"""
    recommendations = []
    
    if risk_factors["critical_emergencies"] > 0:
        recommendations.append("Deploy additional emergency response teams")
        recommendations.append("Consider partial event suspension")
    
    if risk_factors["active_emergencies"] > 3:
        recommendations.append("Increase medical personnel on standby")
        recommendations.append("Enhance crowd monitoring")
    
    if risk_factors["attendance_ratio"] > 0.9:
        recommendations.append("Implement crowd control measures")
        recommendations.append("Monitor entry points closely")
    
    if risk_factors["weather_risk"] > 0.5:
        recommendations.append("Monitor weather conditions closely")
        recommendations.append("Prepare weather contingency plans")
    
    if not recommendations:
        recommendations.append("Continue normal monitoring procedures")
    
    return recommendations

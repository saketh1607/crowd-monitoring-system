"""
Sensor management API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from src.data.database import get_db
from src.data.models import Sensor, SensorReading, SensorCreate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/")
async def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """Register a new sensor"""
    try:
        db_sensor = Sensor(**sensor.dict())
        db.add(db_sensor)
        db.commit()
        db.refresh(db_sensor)
        
        logger.info(f"Sensor created: {db_sensor.sensor_id}")
        return db_sensor
        
    except Exception as e:
        logger.error(f"Error creating sensor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/readings/")
async def submit_sensor_reading(reading: SensorReading, db: Session = Depends(get_db)):
    """Submit a sensor reading"""
    try:
        # Find the sensor
        sensor = db.query(Sensor).filter(Sensor.sensor_id == reading.sensor_id).first()
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Create reading record
        from src.data.models import SensorReading as SensorReadingModel
        db_reading = SensorReadingModel(
            sensor_id=sensor.id,
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp or datetime.utcnow(),
            is_anomaly=reading.is_anomaly,
            anomaly_score=reading.anomaly_score
        )
        
        db.add(db_reading)
        
        # Update sensor's last reading
        sensor.last_reading = reading.value
        sensor.last_reading_time = db_reading.timestamp
        
        db.commit()
        
        logger.info(f"Sensor reading recorded: {reading.sensor_id}")
        return {"message": "Reading recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording sensor reading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{sensor_id}/readings")
async def get_sensor_readings(
    sensor_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get sensor readings"""
    try:
        # Find the sensor
        sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        # Query readings
        from src.data.models import SensorReading as SensorReadingModel
        query = db.query(SensorReadingModel).filter(SensorReadingModel.sensor_id == sensor.id)
        
        if start_time:
            query = query.filter(SensorReadingModel.timestamp >= start_time)
        if end_time:
            query = query.filter(SensorReadingModel.timestamp <= end_time)
        
        readings = query.order_by(SensorReadingModel.timestamp.desc()).limit(limit).all()
        
        return readings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sensor readings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_sensors(
    event_id: Optional[int] = None,
    sensor_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of sensors"""
    try:
        query = db.query(Sensor)
        
        if event_id:
            query = query.filter(Sensor.event_id == event_id)
        if sensor_type:
            query = query.filter(Sensor.sensor_type == sensor_type)
        if is_active is not None:
            query = query.filter(Sensor.is_active == is_active)
        
        sensors = query.all()
        return sensors
        
    except Exception as e:
        logger.error(f"Error fetching sensors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

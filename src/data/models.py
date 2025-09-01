"""
Data models for the Emergency Management System
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class EmergencyType(str, Enum):
    """Types of emergencies"""
    MEDICAL = "medical"
    FIRE = "fire"
    SECURITY = "security"


class EmergencyStatus(str, Enum):
    """Status of emergency incidents"""
    DETECTED = "detected"
    CONFIRMED = "confirmed"
    RESPONDING = "responding"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class SeverityLevel(str, Enum):
    """Severity levels for emergencies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(str, Enum):
    """Types of emergency response resources"""
    MEDICAL_PERSONNEL = "medical_personnel"
    FIRE_PERSONNEL = "fire_personnel"
    SECURITY_PERSONNEL = "security_personnel"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE_CAR = "police_car"
    EQUIPMENT = "equipment"


# SQLAlchemy Models
class Event(Base):
    """Large event/gathering information"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    venue = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    expected_attendance = Column(Integer)
    actual_attendance = Column(Integer)
    weather_conditions = Column(JSON)
    risk_level = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emergencies = relationship("Emergency", back_populates="event")
    sensors = relationship("Sensor", back_populates="event")


class Emergency(Base):
    """Emergency incident records"""
    __tablename__ = "emergencies"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    type = Column(String, nullable=False)  # EmergencyType
    status = Column(String, default="detected")  # EmergencyStatus
    severity = Column(String, default="medium")  # SeverityLevel
    location_x = Column(Float)  # Coordinates within venue
    location_y = Column(Float)
    location_description = Column(String)
    description = Column(Text)
    confidence_score = Column(Float)  # ML model confidence
    detection_source = Column(String)  # camera, sensor, manual, etc.
    detected_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    resolved_at = Column(DateTime)
    response_time = Column(Integer)  # seconds
    emergency_metadata = Column(JSON)  # Additional emergency-specific data
    
    # Relationships
    event = relationship("Event", back_populates="emergencies")
    responses = relationship("EmergencyResponse", back_populates="emergency")


class Sensor(Base):
    """IoT sensor information and readings"""
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    sensor_id = Column(String, unique=True, nullable=False)
    sensor_type = Column(String, nullable=False)  # temperature, smoke, sound, motion
    location_x = Column(Float)
    location_y = Column(Float)
    location_description = Column(String)
    is_active = Column(Boolean, default=True)
    last_reading = Column(Float)
    last_reading_time = Column(DateTime)
    alert_threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    event = relationship("Event", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor")


class SensorReading(Base):
    """Individual sensor readings"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float)
    
    # Relationships
    sensor = relationship("Sensor", back_populates="readings")


class Resource(Base):
    """Emergency response resources"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # ResourceType
    capacity = Column(Integer)
    current_location_x = Column(Float)
    current_location_y = Column(Float)
    is_available = Column(Boolean, default=True)
    contact_info = Column(JSON)
    capabilities = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = relationship("EmergencyResponse", back_populates="resource")


class EmergencyResponse(Base):
    """Emergency response actions and resource deployment"""
    __tablename__ = "emergency_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    emergency_id = Column(Integer, ForeignKey("emergencies.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    arrived_at = Column(DateTime)
    completed_at = Column(DateTime)
    response_notes = Column(Text)
    effectiveness_score = Column(Float)
    
    # Relationships
    emergency = relationship("Emergency", back_populates="responses")
    resource = relationship("Resource", back_populates="responses")


# Pydantic Models for API
class EventBase(BaseModel):
    """Base event model"""
    name: str
    description: Optional[str] = None
    venue: str
    start_time: datetime
    end_time: datetime
    expected_attendance: Optional[int] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    risk_level: str = "medium"


class EventCreate(EventBase):
    """Event creation model"""
    pass


class EventUpdate(BaseModel):
    """Event update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    actual_attendance: Optional[int] = None
    weather_conditions: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = None


class EventResponse(EventBase):
    """Event response model"""
    id: int
    actual_attendance: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmergencyBase(BaseModel):
    """Base emergency model"""
    type: EmergencyType
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    location_description: Optional[str] = None
    description: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.MEDIUM
    detection_source: Optional[str] = None
    emergency_metadata: Optional[Dict[str, Any]] = None


class EmergencyCreate(EmergencyBase):
    """Emergency creation model"""
    event_id: int
    confidence_score: Optional[float] = None


class EmergencyUpdate(BaseModel):
    """Emergency update model"""
    status: Optional[EmergencyStatus] = None
    severity: Optional[SeverityLevel] = None
    description: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class EmergencyResponse(EmergencyBase):
    """Emergency response model"""
    id: int
    event_id: int
    status: EmergencyStatus
    confidence_score: Optional[float] = None
    detected_at: datetime
    confirmed_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_time: Optional[int] = None
    
    class Config:
        from_attributes = True


class SensorBase(BaseModel):
    """Base sensor model"""
    sensor_id: str
    sensor_type: str
    location_x: Optional[float] = None
    location_y: Optional[float] = None
    location_description: Optional[str] = None
    alert_threshold: Optional[float] = None


class SensorCreate(SensorBase):
    """Sensor creation model"""
    event_id: int


class SensorReading(BaseModel):
    """Sensor reading model"""
    sensor_id: str
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
    is_anomaly: bool = False
    anomaly_score: Optional[float] = None


class ResourceBase(BaseModel):
    """Base resource model"""
    name: str
    type: ResourceType
    capacity: Optional[int] = None
    current_location_x: Optional[float] = None
    current_location_y: Optional[float] = None
    contact_info: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None


class ResourceCreate(ResourceBase):
    """Resource creation model"""
    pass


class ResourceResponse(ResourceBase):
    """Resource response model"""
    id: int
    is_available: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

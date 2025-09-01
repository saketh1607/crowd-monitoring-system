"""
Configuration settings for the Emergency Management System
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application
    APP_NAME: str = "Emergency Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # Database Configuration - Using SQLite for local development
    DATABASE_URL: str = "sqlite:///./emergency_management.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EMERGENCY_TOPIC: str = "emergency_events"
    KAFKA_SENSOR_TOPIC: str = "sensor_data"
    
    # ML Model Configuration
    MODEL_PATH: str = "data/models"
    MODEL_UPDATE_INTERVAL: int = 3600  # 1 hour
    PREDICTION_THRESHOLD: float = 0.7
    
    # Emergency Detection Thresholds
    MEDICAL_EMERGENCY_THRESHOLD: float = 0.8
    FIRE_DETECTION_THRESHOLD: float = 0.85
    SECURITY_THREAT_THRESHOLD: float = 0.75
    
    # Crowd Monitoring
    MAX_CROWD_DENSITY: int = 4  # people per square meter
    CROWD_ALERT_THRESHOLD: float = 0.8  # 80% of max capacity
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    
    # Notification Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    EMERGENCY_CONTACTS: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # Monitoring and Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 8001
    
    # File Storage
    UPLOAD_PATH: str = "data/uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = ".jpg,.jpeg,.png,.mp4,.avi"
    
    # Camera and Sensor Configuration
    CAMERA_URLS: str = ""
    SENSOR_UPDATE_INTERVAL: int = 5  # seconds
    
    # Dashboard Configuration
    DASHBOARD_REFRESH_INTERVAL: int = 2  # seconds
    MAX_DASHBOARD_HISTORY: int = 1000  # number of events to keep in memory
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    # Validators removed for simplicity - can be added back later if needed


# Global settings instance
settings = Settings()


# Emergency Type Configurations
EMERGENCY_TYPES = {
    "medical": {
        "name": "Medical Emergency",
        "priority": 1,
        "response_time": 300,  # 5 minutes
        "required_personnel": ["paramedic", "doctor"],
        "equipment": ["ambulance", "medical_kit", "defibrillator"]
    },
    "fire": {
        "name": "Fire Outbreak",
        "priority": 1,
        "response_time": 180,  # 3 minutes
        "required_personnel": ["firefighter", "fire_chief"],
        "equipment": ["fire_truck", "extinguisher", "hose"]
    },
    "security": {
        "name": "Security Threat",
        "priority": 2,
        "response_time": 120,  # 2 minutes
        "required_personnel": ["security_officer", "police"],
        "equipment": ["radio", "restraints", "protective_gear"]
    }
}

# Sensor Type Configurations
SENSOR_TYPES = {
    "temperature": {
        "unit": "celsius",
        "normal_range": (15, 30),
        "alert_threshold": 40
    },
    "smoke": {
        "unit": "ppm",
        "normal_range": (0, 10),
        "alert_threshold": 50
    },
    "sound": {
        "unit": "decibels",
        "normal_range": (40, 85),
        "alert_threshold": 100
    },
    "motion": {
        "unit": "count",
        "normal_range": (0, 100),
        "alert_threshold": 200
    }
}

# ML Model Configurations
MODEL_CONFIGS = {
    "crowd_density": {
        "model_type": "cnn",
        "input_shape": (224, 224, 3),
        "output_classes": 5
    },
    "fire_detection": {
        "model_type": "yolo",
        "confidence_threshold": 0.5,
        "nms_threshold": 0.4
    },
    "behavior_analysis": {
        "model_type": "lstm",
        "sequence_length": 30,
        "features": 15
    }
}

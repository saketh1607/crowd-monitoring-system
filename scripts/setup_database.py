#!/usr/bin/env python3
"""
Database setup script for Emergency Management System
"""
import os
import sys
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from src.data.models import Base, Event, Resource, Sensor
from src.data.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample data for testing"""
    logger.info("Creating sample data...")
    
    # Create database engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Sample Events
        events = [
            Event(
                name="Summer Music Festival 2024",
                description="Large outdoor music festival with multiple stages",
                venue="Central Park Amphitheater",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=3),
                expected_attendance=50000,
                actual_attendance=45000,
                weather_conditions={
                    "temperature": 25,
                    "humidity": 60,
                    "wind_speed": 10,
                    "precipitation": 0
                },
                risk_level="medium"
            ),
            Event(
                name="Tech Conference 2024",
                description="Indoor technology conference and expo",
                venue="Convention Center Hall A",
                start_time=datetime.utcnow() + timedelta(days=7),
                end_time=datetime.utcnow() + timedelta(days=9),
                expected_attendance=15000,
                weather_conditions={
                    "temperature": 22,
                    "humidity": 45,
                    "wind_speed": 5,
                    "precipitation": 0
                },
                risk_level="low"
            ),
            Event(
                name="Sports Championship Final",
                description="Major sports championship final game",
                venue="National Stadium",
                start_time=datetime.utcnow() + timedelta(days=14),
                end_time=datetime.utcnow() + timedelta(days=14, hours=4),
                expected_attendance=80000,
                weather_conditions={
                    "temperature": 18,
                    "humidity": 70,
                    "wind_speed": 15,
                    "precipitation": 5
                },
                risk_level="high"
            )
        ]
        
        for event in events:
            db.add(event)
        
        db.commit()
        
        # Get event IDs for resources and sensors
        event_ids = [event.id for event in events]
        
        # Sample Resources
        resources = [
            # Medical Resources
            Resource(
                name="Ambulance Unit 1",
                type="ambulance",
                capacity=2,
                current_location_x=100.0,
                current_location_y=200.0,
                is_available=True,
                contact_info={"phone": "+1-555-0101", "radio": "MED-1"},
                capabilities=["emergency_transport", "basic_life_support"]
            ),
            Resource(
                name="Medical Team Alpha",
                type="medical_personnel",
                capacity=4,
                current_location_x=150.0,
                current_location_y=180.0,
                is_available=True,
                contact_info={"phone": "+1-555-0102", "radio": "MED-ALPHA"},
                capabilities=["first_aid", "triage", "advanced_life_support"]
            ),
            
            # Fire Resources
            Resource(
                name="Fire Engine 7",
                type="fire_truck",
                capacity=6,
                current_location_x=300.0,
                current_location_y=250.0,
                is_available=True,
                contact_info={"phone": "+1-555-0201", "radio": "FIRE-7"},
                capabilities=["fire_suppression", "rescue", "hazmat"]
            ),
            Resource(
                name="Fire Team Bravo",
                type="fire_personnel",
                capacity=8,
                current_location_x=320.0,
                current_location_y=230.0,
                is_available=True,
                contact_info={"phone": "+1-555-0202", "radio": "FIRE-BRAVO"},
                capabilities=["fire_fighting", "rescue_operations", "crowd_control"]
            ),
            
            # Security Resources
            Resource(
                name="Security Team 1",
                type="security_personnel",
                capacity=6,
                current_location_x=200.0,
                current_location_y=300.0,
                is_available=True,
                contact_info={"phone": "+1-555-0301", "radio": "SEC-1"},
                capabilities=["crowd_control", "surveillance", "access_control"]
            ),
            Resource(
                name="Police Unit Delta",
                type="police_car",
                capacity=2,
                current_location_x=180.0,
                current_location_y=320.0,
                is_available=True,
                contact_info={"phone": "+1-555-0302", "radio": "POLICE-DELTA"},
                capabilities=["law_enforcement", "traffic_control", "emergency_response"]
            )
        ]
        
        for resource in resources:
            db.add(resource)
        
        db.commit()
        
        # Sample Sensors for each event
        sensor_types = ["temperature", "smoke", "sound", "motion"]
        sensor_locations = [
            (50, 50), (150, 50), (250, 50),
            (50, 150), (150, 150), (250, 150),
            (50, 250), (150, 250), (250, 250)
        ]
        
        for event_id in event_ids:
            for i, (x, y) in enumerate(sensor_locations):
                for sensor_type in sensor_types:
                    sensor = Sensor(
                        event_id=event_id,
                        sensor_id=f"SENSOR_{event_id}_{sensor_type}_{i+1:03d}",
                        sensor_type=sensor_type,
                        location_x=x,
                        location_y=y,
                        location_description=f"Zone {i+1}",
                        is_active=True,
                        alert_threshold=get_sensor_threshold(sensor_type),
                        last_reading=get_normal_reading(sensor_type),
                        last_reading_time=datetime.utcnow()
                    )
                    db.add(sensor)
        
        db.commit()
        
        logger.info("Sample data created successfully!")
        logger.info(f"Created {len(events)} events")
        logger.info(f"Created {len(resources)} resources")
        logger.info(f"Created {len(event_ids) * len(sensor_locations) * len(sensor_types)} sensors")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_sensor_threshold(sensor_type):
    """Get appropriate threshold for sensor type"""
    thresholds = {
        "temperature": 35.0,  # Celsius
        "smoke": 50.0,        # PPM
        "sound": 85.0,        # Decibels
        "motion": 100.0       # Motion units
    }
    return thresholds.get(sensor_type, 50.0)


def get_normal_reading(sensor_type):
    """Get normal reading for sensor type"""
    import random
    
    normal_ranges = {
        "temperature": (18, 25),
        "smoke": (0, 5),
        "sound": (45, 70),
        "motion": (5, 25)
    }
    
    min_val, max_val = normal_ranges.get(sensor_type, (0, 50))
    return random.uniform(min_val, max_val)


def main():
    """Main setup function"""
    logger.info("Starting database setup...")
    
    try:
        # Initialize database (create tables)
        init_db()
        logger.info("Database tables created successfully!")
        
        # Create sample data
        create_sample_data()
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

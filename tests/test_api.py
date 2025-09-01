"""
Tests for Emergency Management API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from src.api.main import app
from src.data.database import get_db
from src.data.models import Base, Event, Emergency, Resource

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and basic endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestEventAPI:
    """Test event management API"""
    
    def setup_method(self):
        """Setup test data"""
        # Clear database
        db = TestingSessionLocal()
        db.query(Event).delete()
        db.commit()
        db.close()
    
    def test_create_event(self):
        """Test creating a new event"""
        event_data = {
            "name": "Test Music Festival",
            "description": "A test music festival",
            "venue": "Test Venue",
            "start_time": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "expected_attendance": 10000,
            "risk_level": "medium"
        }
        
        response = client.post("/api/v1/events/", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == event_data["name"]
        assert data["venue"] == event_data["venue"]
        assert "id" in data
    
    def test_get_events(self):
        """Test retrieving events"""
        # First create an event
        event_data = {
            "name": "Test Event",
            "venue": "Test Venue",
            "start_time": datetime.utcnow().isoformat(),
            "end_time": (datetime.utcnow() + timedelta(hours=4)).isoformat()
        }
        
        create_response = client.post("/api/v1/events/", json=event_data)
        assert create_response.status_code == 200
        
        # Get events
        response = client.get("/api/v1/events/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_event_by_id(self):
        """Test retrieving specific event"""
        # Create event first
        event_data = {
            "name": "Specific Test Event",
            "venue": "Specific Venue",
            "start_time": datetime.utcnow().isoformat(),
            "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }
        
        create_response = client.post("/api/v1/events/", json=event_data)
        event_id = create_response.json()["id"]
        
        # Get specific event
        response = client.get(f"/api/v1/events/{event_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == event_id
        assert data["name"] == event_data["name"]
    
    def test_get_nonexistent_event(self):
        """Test retrieving non-existent event"""
        response = client.get("/api/v1/events/99999")
        assert response.status_code == 404


class TestEmergencyAPI:
    """Test emergency management API"""
    
    def setup_method(self):
        """Setup test data"""
        db = TestingSessionLocal()
        
        # Clear existing data
        db.query(Emergency).delete()
        db.query(Event).delete()
        
        # Create test event
        test_event = Event(
            name="Test Event for Emergency",
            venue="Test Venue",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=4)
        )
        db.add(test_event)
        db.commit()
        db.refresh(test_event)
        
        self.test_event_id = test_event.id
        db.close()
    
    def test_create_emergency(self):
        """Test creating emergency"""
        emergency_data = {
            "event_id": self.test_event_id,
            "type": "medical",
            "severity": "high",
            "location_x": 100.0,
            "location_y": 200.0,
            "description": "Medical emergency in crowd",
            "detection_source": "manual"
        }
        
        response = client.post("/api/v1/emergencies/", json=emergency_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["type"] == "medical"
        assert data["severity"] == "high"
        assert data["event_id"] == self.test_event_id
    
    def test_get_emergencies(self):
        """Test retrieving emergencies"""
        # Create emergency first
        emergency_data = {
            "event_id": self.test_event_id,
            "type": "fire",
            "severity": "critical",
            "location_x": 50.0,
            "location_y": 75.0
        }
        
        create_response = client.post("/api/v1/emergencies/", json=emergency_data)
        assert create_response.status_code == 200
        
        # Get emergencies
        response = client.get("/api/v1/emergencies/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_update_emergency(self):
        """Test updating emergency status"""
        # Create emergency
        emergency_data = {
            "event_id": self.test_event_id,
            "type": "security",
            "severity": "medium"
        }
        
        create_response = client.post("/api/v1/emergencies/", json=emergency_data)
        emergency_id = create_response.json()["id"]
        
        # Update emergency
        update_data = {
            "status": "responding",
            "severity": "high"
        }
        
        response = client.put(f"/api/v1/emergencies/{emergency_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "responding"
        assert data["severity"] == "high"
    
    def test_fire_detection_endpoint(self):
        """Test fire detection endpoint"""
        image_data = {
            "image": "base64_encoded_image_data_here",
            "metadata": {"camera_id": "CAM_001"}
        }
        
        response = client.post("/api/v1/emergencies/detect/fire", json=image_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "fire_detected" in data
        assert "confidence" in data
        assert "timestamp" in data
    
    def test_crowd_analysis_endpoint(self):
        """Test crowd analysis endpoint"""
        image_data = {
            "image": "base64_encoded_image_data_here",
            "area_sqm": 100.0
        }
        
        response = client.post("/api/v1/emergencies/analyze/crowd", json=image_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "people_count" in data
        assert "density_per_sqm" in data
        assert "density_level" in data
    
    def test_behavior_analysis_endpoint(self):
        """Test behavior analysis endpoint"""
        sensor_data = {
            "motion": [1, 2, 3, 4, 5],
            "audio": [60, 65, 70, 75, 80],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = client.post("/api/v1/emergencies/analyze/behavior", json=sensor_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "threat_detected" in data
        assert "confidence" in data
        assert "behavior_type" in data


class TestResourceAPI:
    """Test resource management API"""
    
    def setup_method(self):
        """Setup test data"""
        db = TestingSessionLocal()
        db.query(Resource).delete()
        db.commit()
        db.close()
    
    def test_create_resource(self):
        """Test creating a resource"""
        resource_data = {
            "name": "Test Ambulance",
            "type": "ambulance",
            "capacity": 2,
            "current_location_x": 100.0,
            "current_location_y": 150.0,
            "contact_info": {"phone": "+1-555-0123"},
            "capabilities": ["emergency_transport", "basic_life_support"]
        }
        
        response = client.post("/api/v1/resources/", json=resource_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Ambulance"
        assert data["type"] == "ambulance"
        assert data["is_available"] is True
    
    def test_get_resources(self):
        """Test retrieving resources"""
        # Create resource first
        resource_data = {
            "name": "Test Fire Truck",
            "type": "fire_truck",
            "capacity": 6
        }
        
        create_response = client.post("/api/v1/resources/", json=resource_data)
        assert create_response.status_code == 200
        
        # Get resources
        response = client.get("/api/v1/resources/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_filter_available_resources(self):
        """Test filtering available resources"""
        response = client.get("/api/v1/resources/?available=true")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # All returned resources should be available
        for resource in data:
            assert resource["is_available"] is True


class TestResponseOptimization:
    """Test response optimization endpoints"""
    
    def setup_method(self):
        """Setup test data"""
        db = TestingSessionLocal()
        
        # Clear and create test data
        db.query(Emergency).delete()
        db.query(Event).delete()
        
        test_event = Event(
            name="Test Event for Response",
            venue="Test Venue",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=4)
        )
        db.add(test_event)
        db.commit()
        db.refresh(test_event)
        
        test_emergency = Emergency(
            event_id=test_event.id,
            type="medical",
            severity="high",
            location_x=100.0,
            location_y=200.0,
            status="detected"
        )
        db.add(test_emergency)
        db.commit()
        db.refresh(test_emergency)
        
        self.test_emergency_id = test_emergency.id
        db.close()
    
    def test_optimize_response(self):
        """Test response optimization"""
        response = client.post(f"/api/v1/emergencies/{self.test_emergency_id}/response")
        assert response.status_code == 200
        
        data = response.json()
        assert "emergency_id" in data
        assert "resource_assignments" in data
        assert "recommendations" in data
        assert "communication_plan" in data
    
    def test_evacuation_planning(self):
        """Test evacuation planning"""
        venue_data = {
            "exits": [
                {"id": "EXIT_1", "name": "Main Exit", "location": [0, 0], "capacity": 1000},
                {"id": "EXIT_2", "name": "Side Exit", "location": [300, 0], "capacity": 500}
            ],
            "zones": {
                "ZONE_1": {"center": [100, 100], "capacity": 500},
                "ZONE_2": {"center": [200, 100], "capacity": 300}
            },
            "crowd_distribution": {
                "ZONE_1": 400,
                "ZONE_2": 250
            }
        }
        
        response = client.post(
            f"/api/v1/emergencies/{self.test_emergency_id}/evacuation",
            json=venue_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "emergency_id" in data
        assert "evacuation_plan" in data
        
        evacuation_plan = data["evacuation_plan"]
        assert "affected_zones" in evacuation_plan
        assert "exit_assignments" in evacuation_plan
        assert "estimated_evacuation_time" in evacuation_plan


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/events/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        incomplete_event = {
            "name": "Incomplete Event"
            # Missing required fields like venue, start_time, end_time
        }
        
        response = client.post("/api/v1/events/", json=incomplete_event)
        assert response.status_code == 422
    
    def test_invalid_emergency_type(self):
        """Test handling of invalid emergency type"""
        emergency_data = {
            "event_id": 1,
            "type": "invalid_type",  # Invalid emergency type
            "severity": "high"
        }
        
        response = client.post("/api/v1/emergencies/", json=emergency_data)
        assert response.status_code == 422


if __name__ == '__main__':
    pytest.main([__file__])

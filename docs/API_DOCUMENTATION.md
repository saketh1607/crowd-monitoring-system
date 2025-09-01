# Emergency Management System - API Documentation

## Overview

The Emergency Management System provides a comprehensive REST API for managing large-scale event emergencies. This API enables real-time emergency detection, resource allocation, and response coordination.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: Bearer Token (JWT)

## Table of Contents

1. [Authentication](#authentication)
2. [Events Management](#events-management)
3. [Emergency Management](#emergency-management)
4. [Resource Management](#resource-management)
5. [Sensor Management](#sensor-management)
6. [Real-time Monitoring](#real-time-monitoring)
7. [ML Detection Services](#ml-detection-services)
8. [Response Optimization](#response-optimization)
9. [WebSocket Events](#websocket-events)
10. [Error Handling](#error-handling)

## Authentication

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Authentication
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Events Management

### Create Event
```http
POST /events/
Content-Type: application/json

{
  "name": "Summer Music Festival 2024",
  "description": "Large outdoor music festival",
  "venue": "Central Park Amphitheater",
  "start_time": "2024-07-15T18:00:00Z",
  "end_time": "2024-07-17T23:00:00Z",
  "expected_attendance": 50000,
  "weather_conditions": {
    "temperature": 25,
    "humidity": 60,
    "wind_speed": 10
  },
  "risk_level": "medium"
}
```

### Get Events
```http
GET /events/
GET /events/?venue=Central Park
GET /events/?risk_level=high
GET /events/?skip=0&limit=10
```

### Get Event by ID
```http
GET /events/{event_id}
```

### Update Event
```http
PUT /events/{event_id}
Content-Type: application/json

{
  "actual_attendance": 45000,
  "risk_level": "high"
}
```

### Delete Event
```http
DELETE /events/{event_id}
```

## Emergency Management

### Create Emergency
```http
POST /emergencies/
Content-Type: application/json

{
  "event_id": 1,
  "type": "medical",
  "severity": "high",
  "location_x": 100.5,
  "location_y": 200.3,
  "location_description": "Main stage area",
  "description": "Person collapsed near stage",
  "detection_source": "manual_report",
  "confidence_score": 0.95
}
```

**Emergency Types:**
- `medical` - Medical emergencies
- `fire` - Fire outbreaks
- `security` - Security threats

**Severity Levels:**
- `low` - Minor incidents
- `medium` - Moderate incidents requiring attention
- `high` - Serious incidents requiring immediate response
- `critical` - Life-threatening situations

### Get Emergencies
```http
GET /emergencies/
GET /emergencies/?event_id=1
GET /emergencies/?status=active
GET /emergencies/?type=medical
GET /emergencies/?severity=critical
```

### Update Emergency Status
```http
PUT /emergencies/{emergency_id}
Content-Type: application/json

{
  "status": "responding",
  "confirmed_at": "2024-07-15T19:30:00Z"
}
```

**Status Values:**
- `detected` - Initially detected
- `confirmed` - Verified by personnel
- `responding` - Response team dispatched
- `resolved` - Incident resolved
- `false_alarm` - False positive

## Resource Management

### Create Resource
```http
POST /resources/
Content-Type: application/json

{
  "name": "Ambulance Unit 1",
  "type": "ambulance",
  "capacity": 2,
  "current_location_x": 150.0,
  "current_location_y": 180.0,
  "contact_info": {
    "phone": "+1-555-0101",
    "radio": "MED-1"
  },
  "capabilities": ["emergency_transport", "basic_life_support"]
}
```

**Resource Types:**
- `medical_personnel` - Medical staff
- `fire_personnel` - Fire fighters
- `security_personnel` - Security officers
- `ambulance` - Emergency vehicles
- `fire_truck` - Fire fighting vehicles
- `police_car` - Police vehicles

### Get Resources
```http
GET /resources/
GET /resources/?type=ambulance
GET /resources/?available=true
GET /resources/?location_radius=100&center_x=150&center_y=200
```

### Update Resource Status
```http
PUT /resources/{resource_id}
Content-Type: application/json

{
  "is_available": false,
  "current_location_x": 200.0,
  "current_location_y": 250.0
}
```

## Sensor Management

### Register Sensor
```http
POST /sensors/
Content-Type: application/json

{
  "event_id": 1,
  "sensor_id": "TEMP_001",
  "sensor_type": "temperature",
  "location_x": 100.0,
  "location_y": 150.0,
  "location_description": "Main entrance",
  "alert_threshold": 35.0
}
```

### Submit Sensor Reading
```http
POST /sensors/readings/
Content-Type: application/json

{
  "sensor_id": "TEMP_001",
  "value": 28.5,
  "unit": "celsius",
  "timestamp": "2024-07-15T19:45:00Z"
}
```

### Get Sensor Data
```http
GET /sensors/{sensor_id}/readings
GET /sensors/{sensor_id}/readings?start_time=2024-07-15T18:00:00Z&end_time=2024-07-15T20:00:00Z
```

## ML Detection Services

### Fire Detection
```http
POST /emergencies/detect/fire
Content-Type: application/json

{
  "image": "base64_encoded_image_data",
  "camera_id": "CAM_001",
  "location": {
    "x": 100.0,
    "y": 200.0
  }
}
```

**Response:**
```json
{
  "fire_detected": true,
  "confidence": 0.87,
  "timestamp": "2024-07-15T19:45:00Z",
  "location": {
    "x": 100.0,
    "y": 200.0
  },
  "camera_id": "CAM_001"
}
```

### Crowd Density Analysis
```http
POST /emergencies/analyze/crowd
Content-Type: application/json

{
  "image": "base64_encoded_image_data",
  "area_sqm": 100.0,
  "camera_id": "CAM_002"
}
```

**Response:**
```json
{
  "people_count": 45,
  "density_per_sqm": 2.3,
  "density_level": "medium",
  "area_sqm": 100.0,
  "people_boxes": [[x, y, w, h], ...],
  "timestamp": "2024-07-15T19:45:00Z"
}
```

### Behavior Analysis
```http
POST /emergencies/analyze/behavior
Content-Type: application/json

{
  "motion_data": [1.2, 2.3, 1.8, 3.1, 2.7],
  "audio_data": [65, 70, 68, 85, 90],
  "location": {
    "x": 150.0,
    "y": 180.0
  }
}
```

**Response:**
```json
{
  "threat_detected": false,
  "confidence": 0.23,
  "behavior_type": "normal",
  "anomaly_score": -0.15,
  "timestamp": "2024-07-15T19:45:00Z"
}
```

## Response Optimization

### Optimize Emergency Response
```http
POST /emergencies/{emergency_id}/response
```

**Response:**
```json
{
  "emergency_id": 1,
  "resource_assignments": {
    "AMBULANCE_1": "EMERGENCY_1",
    "MEDICAL_TEAM_A": "EMERGENCY_1"
  },
  "recommendations": [
    {
      "resource_id": "AMBULANCE_1",
      "estimated_response_time": 180,
      "priority": 1
    }
  ],
  "communication_plan": {
    "notifications": [
      {
        "audience": "emergency_services",
        "message": "Medical emergency at location (100, 200)",
        "method": "direct_call",
        "priority": 1
      }
    ]
  }
}
```

### Plan Evacuation
```http
POST /emergencies/{emergency_id}/evacuation
Content-Type: application/json

{
  "exits": [
    {
      "id": "EXIT_1",
      "name": "Main Exit",
      "location": [0, 0],
      "capacity": 1000
    }
  ],
  "zones": {
    "ZONE_1": {
      "center": [100, 100],
      "capacity": 500
    }
  },
  "crowd_distribution": {
    "ZONE_1": 400
  }
}
```

## Real-time Monitoring

### Get Dashboard Data
```http
GET /monitoring/dashboard
```

**Response:**
```json
{
  "active_emergencies": 3,
  "total_events": 5,
  "available_resources": 12,
  "risk_level": "medium",
  "recent_incidents": [...],
  "system_status": "operational"
}
```

### Get Risk Assessment
```http
GET /monitoring/risk/{event_id}
```

### Get Live Metrics
```http
GET /monitoring/metrics
```

## WebSocket Events

Connect to WebSocket endpoint: `ws://localhost:8000/ws`

### Connection
```javascript
const socket = new WebSocket('ws://localhost:8000/ws');

socket.onopen = function(event) {
    console.log('Connected to Emergency Management System');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleRealtimeUpdate(data);
};
```

### Event Types

#### Emergency Alert
```json
{
  "type": "emergency_alert",
  "priority": "high",
  "data": {
    "emergency_id": 1,
    "type": "fire",
    "severity": "critical",
    "location": {"x": 100, "y": 200},
    "timestamp": "2024-07-15T19:45:00Z"
  }
}
```

#### Emergency Created
```json
{
  "type": "emergency_created",
  "data": {
    "id": 1,
    "type": "medical",
    "severity": "high",
    "location": {"x": 150, "y": 180}
  }
}
```

#### Emergency Updated
```json
{
  "type": "emergency_updated",
  "data": {
    "id": 1,
    "status": "responding",
    "timestamp": "2024-07-15T19:50:00Z"
  }
}
```

#### Status Update
```json
{
  "type": "status_update",
  "data": {
    "active_emergencies": 2,
    "available_resources": 10,
    "system_status": "operational"
  }
}
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Error Response Format
```json
{
  "error": "Validation Error",
  "message": "Invalid emergency type provided",
  "details": {
    "field": "type",
    "value": "invalid_type",
    "allowed_values": ["medical", "fire", "security"]
  },
  "timestamp": "2024-07-15T19:45:00Z"
}
```

### Common Error Scenarios

1. **Invalid Emergency Type**
   ```json
   {
     "error": "Validation Error",
     "message": "Emergency type must be one of: medical, fire, security"
   }
   ```

2. **Resource Not Available**
   ```json
   {
     "error": "Resource Conflict",
     "message": "Resource AMBULANCE_1 is already assigned to another emergency"
   }
   ```

3. **Event Not Found**
   ```json
   {
     "error": "Not Found",
     "message": "Event with ID 999 does not exist"
   }
   ```

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **General endpoints**: 100 requests per minute
- **ML detection endpoints**: 10 requests per minute
- **WebSocket connections**: 5 connections per IP

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

## SDK Examples

### Python SDK
```python
import requests

class EmergencyAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def create_emergency(self, emergency_data):
        response = requests.post(
            f"{self.base_url}/emergencies/",
            json=emergency_data,
            headers=self.headers
        )
        return response.json()
    
    def get_emergencies(self, **filters):
        response = requests.get(
            f"{self.base_url}/emergencies/",
            params=filters,
            headers=self.headers
        )
        return response.json()

# Usage
api = EmergencyAPI("http://localhost:8000/api/v1", "your_token")
emergency = api.create_emergency({
    "event_id": 1,
    "type": "medical",
    "severity": "high"
})
```

### JavaScript SDK
```javascript
class EmergencyAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createEmergency(emergencyData) {
        const response = await fetch(`${this.baseUrl}/emergencies/`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(emergencyData)
        });
        return response.json();
    }
    
    async getEmergencies(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${this.baseUrl}/emergencies/?${params}`, {
            headers: this.headers
        });
        return response.json();
    }
}

// Usage
const api = new EmergencyAPI('http://localhost:8000/api/v1', 'your_token');
const emergency = await api.createEmergency({
    event_id: 1,
    type: 'medical',
    severity: 'high'
});
```

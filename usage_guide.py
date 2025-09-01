"""
Emergency Management System - Complete Usage Guide
This script demonstrates all the ways to use your emergency management system
"""
import requests
import json
import time
from datetime import datetime, timedelta

# Base URL for your API
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/v1"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_response(response, title="Response"):
    """Print formatted API response"""
    if response.status_code == 200:
        print(f"✅ {title}: SUCCESS")
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ {title}: FAILED (Status: {response.status_code})")
        print(response.text)

# ============================================================================
# 1. SYSTEM HEALTH AND STATUS
# ============================================================================

def check_system_health():
    """Check if the system is running properly"""
    print_section("1. SYSTEM HEALTH CHECK")
    
    # Basic health check
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    
    # Dashboard overview
    response = requests.get(f"{API_URL}/monitoring/dashboard")
    print_response(response, "Dashboard Status")

# ============================================================================
# 2. EVENT MANAGEMENT
# ============================================================================

def manage_events():
    """Demonstrate event creation and management"""
    print_section("2. EVENT MANAGEMENT")
    
    # Create a new event
    print("\n📅 Creating a new event...")
    event_data = {
        "name": "Rock Concert 2025",
        "description": "Large outdoor rock concert with multiple bands",
        "venue": "City Stadium",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=8)).isoformat(),
        "expected_attendance": 25000,
        "risk_level": "medium"
    }
    
    response = requests.post(f"{API_URL}/events/", json=event_data)
    print_response(response, "Event Creation")
    
    if response.status_code == 200:
        event_id = response.json()["id"]
        print(f"📝 Event created with ID: {event_id}")
        
        # Get all events
        print("\n📋 Getting all events...")
        response = requests.get(f"{API_URL}/events/")
        print_response(response, "All Events")
        
        return event_id
    
    return None

# ============================================================================
# 3. EMERGENCY DETECTION (AI-POWERED)
# ============================================================================

def demonstrate_emergency_detection():
    """Demonstrate AI-powered emergency detection"""
    print_section("3. AI EMERGENCY DETECTION")
    
    # 🔥 FIRE DETECTION
    print("\n🔥 Testing Fire Detection...")
    fire_data = {
        "image": "base64_encoded_camera_feed_data",
        "camera_id": "CAM_MAIN_STAGE",
        "location": {"x": 150.0, "y": 200.0}
    }
    
    response = requests.post(f"{API_URL}/emergencies/detect/fire", json=fire_data)
    print_response(response, "Fire Detection")
    
    # 👥 CROWD DENSITY ANALYSIS
    print("\n👥 Testing Crowd Density Analysis...")
    crowd_data = {
        "image": "base64_encoded_crowd_image",
        "area_sqm": 200.0,
        "camera_id": "CAM_ENTRANCE_GATE"
    }
    
    response = requests.post(f"{API_URL}/emergencies/analyze/crowd", json=crowd_data)
    print_response(response, "Crowd Analysis")
    
    # 🚨 BEHAVIOR ANALYSIS
    print("\n🚨 Testing Behavior Analysis...")
    behavior_data = {
        "motion_data": [15, 20, 25, 30, 35],  # Motion sensor readings
        "audio_data": [75, 80, 85, 90, 95],   # Audio level readings
        "location": {"x": 300.0, "y": 400.0}
    }
    
    response = requests.post(f"{API_URL}/emergencies/analyze/behavior", json=behavior_data)
    print_response(response, "Behavior Analysis")

# ============================================================================
# 4. EMERGENCY MANAGEMENT
# ============================================================================

def manage_emergencies(event_id=None):
    """Demonstrate emergency incident management"""
    print_section("4. EMERGENCY INCIDENT MANAGEMENT")
    
    # Create a manual emergency report
    print("\n🚨 Creating a manual emergency report...")
    emergency_data = {
        "event_id": event_id or 1,
        "type": "medical",
        "severity": "high",
        "location_x": 125.5,
        "location_y": 250.3,
        "description": "Person experiencing chest pain near food court",
        "detection_source": "security_guard_report"
    }
    
    response = requests.post(f"{API_URL}/emergencies/", json=emergency_data)
    print_response(response, "Emergency Creation")
    
    if response.status_code == 200:
        emergency_id = response.json()["id"]
        print(f"🆔 Emergency created with ID: {emergency_id}")
        
        # Get all emergencies
        print("\n📋 Getting all emergencies...")
        response = requests.get(f"{API_URL}/emergencies/")
        print_response(response, "All Emergencies")
        
        return emergency_id
    
    return None

# ============================================================================
# 5. REAL-TIME MONITORING
# ============================================================================

def monitor_system():
    """Demonstrate real-time system monitoring"""
    print_section("5. REAL-TIME SYSTEM MONITORING")
    
    print("📊 Getting current system status...")
    response = requests.get(f"{API_URL}/monitoring/dashboard")
    
    if response.status_code == 200:
        dashboard = response.json()
        
        print("📈 CURRENT SYSTEM STATUS:")
        print(f"  🚨 Active Emergencies: {dashboard.get('active_emergencies', 0)}")
        print(f"  📅 Total Events: {dashboard.get('total_events', 0)}")
        print(f"  🚑 Available Resources: {dashboard.get('available_resources', 0)}")
        print(f"  📡 Active Sensors: {dashboard.get('active_sensors', 0)}")
        print(f"  ⚠️ Risk Level: {dashboard.get('risk_level', 'unknown').upper()}")
        
        # Show recent emergencies
        recent = dashboard.get('recent_emergencies', [])
        if recent:
            print(f"\n🕐 Recent Emergencies:")
            for emergency in recent[:3]:
                print(f"  #{emergency.get('id')}: {emergency.get('type')} ({emergency.get('severity')})")
    else:
        print("❌ Failed to get dashboard data")

# ============================================================================
# 6. ADVANCED SCENARIOS
# ============================================================================

def simulate_emergency_scenarios():
    """Simulate various emergency scenarios"""
    print_section("6. EMERGENCY SCENARIO SIMULATIONS")
    
    scenarios = [
        {
            "name": "🔥 Fire Emergency",
            "endpoint": f"{API_URL}/emergencies/detect/fire",
            "data": {
                "image": "fire_detected_base64",
                "camera_id": "CAM_BACKSTAGE",
                "location": {"x": 400, "y": 300}
            }
        },
        {
            "name": "👥 Overcrowding Alert",
            "endpoint": f"{API_URL}/emergencies/analyze/crowd",
            "data": {
                "image": "crowded_area_base64",
                "area_sqm": 50.0,
                "camera_id": "CAM_VIP_SECTION"
            }
        },
        {
            "name": "🚨 Security Threat",
            "endpoint": f"{API_URL}/emergencies/analyze/behavior",
            "data": {
                "motion_data": [25, 30, 35, 40, 45],  # High motion
                "audio_data": [95, 100, 105, 110, 115],  # Very loud
                "location": {"x": 200, "y": 150}
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}...")
        response = requests.post(scenario['endpoint'], json=scenario['data'])
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Detection completed")
            
            # Show key results based on scenario type
            if 'fire_detected' in result:
                print(f"  🔥 Fire detected: {result['fire_detected']}")
                print(f"  📊 Confidence: {result.get('confidence', 0):.2f}")
            elif 'people_count' in result:
                print(f"  👥 People count: {result['people_count']}")
                print(f"  📏 Density: {result.get('density_per_sqm', 0):.2f} people/m²")
                print(f"  ⚠️ Level: {result.get('density_level', 'unknown')}")
            elif 'threat_detected' in result:
                print(f"  🚨 Threat detected: {result['threat_detected']}")
                print(f"  🎭 Behavior: {result.get('behavior_type', 'unknown')}")
                print(f"  📊 Confidence: {result.get('confidence', 0):.2f}")
            
            if result.get('emergency_id'):
                print(f"  🆔 Emergency created: ID {result['emergency_id']}")
        else:
            print(f"  ❌ Failed: {response.status_code}")

# ============================================================================
# MAIN USAGE DEMONSTRATION
# ============================================================================

def main():
    """Run complete usage demonstration"""
    print("🎯 EMERGENCY MANAGEMENT SYSTEM - COMPLETE USAGE GUIDE")
    print("This demonstration shows you how to use every feature of your system")
    
    try:
        # 1. Check system health
        check_system_health()
        
        # 2. Manage events
        event_id = manage_events()
        
        # 3. Test emergency detection
        demonstrate_emergency_detection()
        
        # 4. Manage emergencies
        emergency_id = manage_emergencies(event_id)
        
        # 5. Monitor system
        monitor_system()
        
        # 6. Run emergency scenarios
        simulate_emergency_scenarios()
        
        # Final status
        print_section("USAGE DEMONSTRATION COMPLETE")
        print("🎉 You've successfully tested all system features!")
        print("\n🔗 Quick Access Links:")
        print(f"  📖 API Documentation: {BASE_URL}/docs")
        print(f"  ❤️ Health Check: {BASE_URL}/health")
        print(f"  📊 Dashboard Data: {API_URL}/monitoring/dashboard")
        
        print("\n📱 Next Steps:")
        print("  1. Use the interactive API docs to test more scenarios")
        print("  2. Integrate with your cameras and sensors")
        print("  3. Build a web dashboard for real-time monitoring")
        print("  4. Connect to emergency services for automated alerts")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        print("Make sure your server is running at http://127.0.0.1:8000")

if __name__ == "__main__":
    main()

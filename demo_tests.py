"""
Demonstration tests for the Emergency Management System
Shows various emergency detection scenarios
"""
import requests
import json

def test_fire_detection():
    """Test fire detection with various scenarios"""
    print('🔥 Testing Fire Detection...')
    
    # Test with high-risk scenario
    fire_data = {
        'image': 'base64_encoded_fire_image',
        'camera_id': 'CAM_MAIN_STAGE',
        'location': {'x': 150.0, 'y': 200.0}
    }
    
    response = requests.post('http://127.0.0.1:8000/api/v1/emergencies/detect/fire', json=fire_data)
    result = response.json()
    
    print(f'  Fire detected: {result.get("fire_detected")}')
    print(f'  Confidence: {result.get("confidence", 0):.3f}')
    print(f'  Camera: {result.get("camera_id")}')
    
    if result.get('emergency_id'):
        print(f'  🚨 Emergency created: ID {result["emergency_id"]}')
    
    return result

def test_crowd_analysis():
    """Test crowd density analysis"""
    print('\n👥 Testing Crowd Analysis...')
    
    crowd_data = {
        'image': 'base64_encoded_crowd_image',
        'area_sqm': 50.0,
        'camera_id': 'CAM_ENTRANCE'
    }
    
    response = requests.post('http://127.0.0.1:8000/api/v1/emergencies/analyze/crowd', json=crowd_data)
    result = response.json()
    
    print(f'  People count: {result.get("people_count")}')
    print(f'  Density level: {result.get("density_level")}')
    print(f'  Density per m²: {result.get("density_per_sqm")}')
    print(f'  Area: {result.get("area_sqm")} m²')
    
    if result.get('emergency_id'):
        print(f'  🚨 Emergency created: ID {result["emergency_id"]}')
    
    return result

def test_behavior_analysis():
    """Test behavior analysis with suspicious activity"""
    print('\n🚨 Testing Behavior Analysis...')
    
    # Test with suspicious behavior patterns
    behavior_data = {
        'motion_data': [20, 25, 30, 35, 40],  # High motion
        'audio_data': [90, 95, 100, 105, 110],  # High audio
        'location': {'x': 300.0, 'y': 400.0}
    }
    
    response = requests.post('http://127.0.0.1:8000/api/v1/emergencies/analyze/behavior', json=behavior_data)
    result = response.json()
    
    print(f'  Threat detected: {result.get("threat_detected")}')
    print(f'  Behavior type: {result.get("behavior_type")}')
    print(f'  Confidence: {result.get("confidence")}')
    print(f'  Motion avg: {result.get("motion_average")}')
    print(f'  Audio avg: {result.get("audio_average")} dB')
    
    if result.get('emergency_id'):
        print(f'  🚨 Emergency created: ID {result["emergency_id"]}')
    
    return result

def test_dashboard():
    """Test dashboard data"""
    print('\n📊 Dashboard Status...')
    
    response = requests.get('http://127.0.0.1:8000/api/v1/monitoring/dashboard')
    dashboard = response.json()
    
    print(f'  Active emergencies: {dashboard.get("active_emergencies")}')
    print(f'  Risk level: {dashboard.get("risk_level")}')
    print(f'  Total events: {dashboard.get("total_events")}')
    print(f'  Available resources: {dashboard.get("available_resources")}')
    print(f'  Active sensors: {dashboard.get("active_sensors")}')
    
    return dashboard

def test_emergency_management():
    """Test emergency creation and management"""
    print('\n🚨 Testing Emergency Management...')
    
    # Create a medical emergency
    emergency_data = {
        'event_id': 1,
        'type': 'medical',
        'severity': 'high',
        'location_x': 100.0,
        'location_y': 200.0,
        'description': 'Person collapsed near main stage',
        'detection_source': 'manual_report'
    }
    
    response = requests.post('http://127.0.0.1:8000/api/v1/emergencies/', json=emergency_data)
    emergency = response.json()
    
    print(f'  Emergency created: ID {emergency.get("id")}')
    print(f'  Type: {emergency.get("type")}')
    print(f'  Severity: {emergency.get("severity")}')
    print(f'  Location: ({emergency.get("location_x")}, {emergency.get("location_y")})')
    
    return emergency

def main():
    """Run all demonstration tests"""
    print('🎯 Emergency Management System - Live Demonstration')
    print('=' * 60)
    
    try:
        # Test all components
        fire_result = test_fire_detection()
        crowd_result = test_crowd_analysis()
        behavior_result = test_behavior_analysis()
        emergency_result = test_emergency_management()
        dashboard_result = test_dashboard()
        
        print('\n' + '=' * 60)
        print('🎉 DEMONSTRATION COMPLETE!')
        print('=' * 60)
        
        # Summary
        total_emergencies = 0
        if fire_result.get('emergency_id'):
            total_emergencies += 1
        if crowd_result.get('emergency_id'):
            total_emergencies += 1
        if behavior_result.get('emergency_id'):
            total_emergencies += 1
        if emergency_result.get('id'):
            total_emergencies += 1
        
        print(f'\n📊 Session Summary:')
        print(f'  🚨 Emergencies detected: {total_emergencies}')
        print(f'  🔥 Fire detection: {"✅" if fire_result.get("fire_detected") else "❌"}')
        print(f'  👥 Crowd analysis: ✅ {crowd_result.get("people_count", 0)} people')
        print(f'  🚨 Behavior analysis: {"⚠️" if behavior_result.get("threat_detected") else "✅"} {behavior_result.get("behavior_type", "normal")}')
        print(f'  📈 Current risk level: {dashboard_result.get("risk_level", "unknown").upper()}')
        
        print(f'\n🌐 System Access:')
        print(f'  API: http://127.0.0.1:8000')
        print(f'  Documentation: http://127.0.0.1:8000/docs')
        print(f'  Health Check: http://127.0.0.1:8000/health')
        
    except Exception as e:
        print(f'❌ Error during demonstration: {e}')

if __name__ == "__main__":
    main()

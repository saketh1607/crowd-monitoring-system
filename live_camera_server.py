"""
Live Camera Emergency Detection Server
Integrates real camera feeds with the emergency management system
"""
import cv2
import numpy as np
import threading
import time
import requests
import base64
import json
from datetime import datetime
from src.camera.live_detection import LiveCameraDetector, emergency_alert_callback
from src.camera.camera_manager import CameraManager, detect_available_cameras
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveEmergencySystem:
    """Complete live emergency detection system"""
    
    def __init__(self):
        self.camera_manager = CameraManager()
        self.detector = LiveCameraDetector()
        self.running = False
        
        # Statistics
        self.stats = {
            "start_time": None,
            "frames_processed": 0,
            "emergencies_detected": 0,
            "fires_detected": 0,
            "crowd_alerts": 0
        }
        
        # Setup emergency callback
        self.detector.add_emergency_callback(self._emergency_callback)
    
    def _emergency_callback(self, emergency_data):
        """Handle emergency detection"""
        self.stats["emergencies_detected"] += 1
        
        if emergency_data["type"] == "fire":
            self.stats["fires_detected"] += 1
        elif emergency_data["type"] == "crowd":
            self.stats["crowd_alerts"] += 1
        
        # Call the default alert callback
        emergency_alert_callback(emergency_data)
        
        # You can add more actions here:
        # - Send notifications
        # - Trigger alarms
        # - Alert emergency services
        # - Save snapshots
    
    def setup_cameras(self):
        """Setup cameras from configuration"""
        print("🎥 Setting up cameras...")
        
        # Get enabled cameras from configuration
        enabled_cameras = self.camera_manager.get_enabled_cameras()
        
        if not enabled_cameras:
            print("⚠️ No cameras enabled in configuration")
            print("🔍 Detecting available cameras...")
            
            # Auto-detect and setup webcam if available
            available = detect_available_cameras()
            if available:
                camera_id = f"webcam_{available[0]}"
                self.detector.add_camera(
                    camera_id, 
                    available[0], 
                    {"x": 100.0, "y": 200.0}
                )
                print(f"✅ Auto-configured webcam: {camera_id}")
            else:
                print("❌ No cameras detected")
                return False
        else:
            # Setup configured cameras
            for camera_id, config in enabled_cameras.items():
                self.detector.add_camera(
                    camera_id,
                    config["source"],
                    config["location"]
                )
                print(f"✅ Configured camera: {camera_id} - {config['name']}")
        
        return True
    
    def start(self):
        """Start the live detection system"""
        print("🚀 Starting Live Emergency Detection System")
        print("=" * 50)
        
        # Check if API server is running
        if not self._check_api_server():
            print("❌ API server not running. Please start it first:")
            print("   python run_server.py")
            return False
        
        # Setup cameras
        if not self.setup_cameras():
            return False
        
        # Start monitoring
        self.stats["start_time"] = datetime.now()
        self.running = True
        
        try:
            self.detector.start_monitoring()
            print("\n📹 Live camera monitoring started!")
            print("🔥 Watching for fires...")
            print("👥 Monitoring crowd density...")
            print("🚨 Detecting emergencies...")
            print("\nPress Ctrl+C to stop\n")
            
            # Status monitoring loop
            self._status_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping live detection system...")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the live detection system"""
        self.running = False
        self.detector.stop_monitoring()
        print("✅ Live detection system stopped")
    
    def _check_api_server(self) -> bool:
        """Check if the API server is running"""
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _status_loop(self):
        """Main status monitoring loop"""
        while self.running:
            try:
                time.sleep(30)  # Update every 30 seconds
                self._print_status()
            except KeyboardInterrupt:
                break
    
    def _print_status(self):
        """Print current system status"""
        if not self.running:
            return
        
        current_time = datetime.now()
        uptime = current_time - self.stats["start_time"]
        
        print(f"\n📊 System Status - {current_time.strftime('%H:%M:%S')}")
        print(f"⏱️ Uptime: {str(uptime).split('.')[0]}")
        print(f"🚨 Emergencies Detected: {self.stats['emergencies_detected']}")
        print(f"🔥 Fires Detected: {self.stats['fires_detected']}")
        print(f"👥 Crowd Alerts: {self.stats['crowd_alerts']}")
        
        # Camera status
        camera_status = self.detector.get_camera_status()
        print("📹 Camera Status:")
        for camera_id, status in camera_status.items():
            connected = "✅" if status["connected"] else "❌"
            frames = status["frames_processed"]
            print(f"   {camera_id}: {connected} Frames: {frames}")
        
        print("-" * 40)


def setup_demo_cameras():
    """Setup demo cameras for testing"""
    print("🎬 Setting up demo cameras...")
    
    manager = CameraManager()
    
    # Check for available webcams
    available = detect_available_cameras()
    
    if available:
        # Enable the first available webcam
        webcam_config = {
            "name": "Demo Webcam",
            "source": available[0],
            "type": "webcam",
            "location": {"x": 100.0, "y": 200.0},
            "area_sqm": 50.0,
            "enabled": True,
            "detection_types": ["fire", "crowd"],
            "settings": {
                "resolution": [640, 480],
                "fps": 30,
                "detection_interval": 2.0
            }
        }
        
        manager.add_camera("demo_webcam", webcam_config)
        print(f"✅ Demo webcam configured (device {available[0]})")
        return True
    else:
        print("❌ No webcams detected for demo")
        return False


def main():
    """Main function to run live detection system"""
    print("🎥 Live Camera Emergency Detection System")
    print("🚨 Real-time AI-powered emergency detection")
    print("=" * 60)
    
    # Check for cameras
    available_cameras = detect_available_cameras()
    print(f"📹 Available cameras detected: {available_cameras}")
    
    if not available_cameras:
        print("\n⚠️ No cameras detected!")
        print("📝 To use this system:")
        print("   1. Connect a webcam or USB camera")
        print("   2. Configure IP cameras in config/cameras.json")
        print("   3. Ensure camera permissions are granted")
        return
    
    # Setup demo if needed
    manager = CameraManager()
    enabled_cameras = manager.get_enabled_cameras()
    
    if not enabled_cameras:
        print("\n🎬 No cameras configured. Setting up demo...")
        if not setup_demo_cameras():
            return
    
    # Create and start the system
    system = LiveEmergencySystem()
    
    print(f"\n🔗 Make sure your API server is running:")
    print(f"   python run_server.py")
    print(f"   API: http://127.0.0.1:8000")
    
    # Start the live detection
    system.start()


if __name__ == "__main__":
    main()

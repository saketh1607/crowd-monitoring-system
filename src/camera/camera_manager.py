"""
Camera Management System for Live Emergency Detection
Handles multiple camera sources and configurations
"""
import cv2
import json
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CameraManager:
    """Manages camera configurations and connections"""
    
    def __init__(self, config_file: str = "config/cameras.json"):
        self.config_file = config_file
        self.cameras = {}
        self.load_camera_config()
    
    def load_camera_config(self):
        """Load camera configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.cameras = json.load(f)
                logger.info(f"Loaded {len(self.cameras)} camera configurations")
            except Exception as e:
                logger.error(f"Error loading camera config: {e}")
                self.cameras = {}
        else:
            # Create default configuration
            self.create_default_config()
    
    def create_default_config(self):
        """Create default camera configuration"""
        self.cameras = {
            "webcam_main": {
                "name": "Main Webcam",
                "source": 0,
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
            },
            "entrance_cam": {
                "name": "Entrance Camera",
                "source": "http://192.168.1.100:8080/video",
                "type": "ip_camera",
                "location": {"x": 0.0, "y": 0.0},
                "area_sqm": 100.0,
                "enabled": False,
                "detection_types": ["crowd", "behavior"],
                "settings": {
                    "resolution": [1280, 720],
                    "fps": 15,
                    "detection_interval": 3.0
                }
            },
            "stage_cam": {
                "name": "Main Stage Camera",
                "source": "http://192.168.1.101:8080/video",
                "type": "ip_camera",
                "location": {"x": 500.0, "y": 300.0},
                "area_sqm": 200.0,
                "enabled": False,
                "detection_types": ["fire", "crowd"],
                "settings": {
                    "resolution": [1920, 1080],
                    "fps": 10,
                    "detection_interval": 1.0
                }
            }
        }
        self.save_camera_config()
    
    def save_camera_config(self):
        """Save camera configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.cameras, f, indent=2)
            logger.info("Camera configuration saved")
        except Exception as e:
            logger.error(f"Error saving camera config: {e}")
    
    def add_camera(self, camera_id: str, config: Dict):
        """Add a new camera configuration"""
        self.cameras[camera_id] = config
        self.save_camera_config()
        logger.info(f"Added camera: {camera_id}")
    
    def remove_camera(self, camera_id: str):
        """Remove a camera configuration"""
        if camera_id in self.cameras:
            del self.cameras[camera_id]
            self.save_camera_config()
            logger.info(f"Removed camera: {camera_id}")
    
    def get_enabled_cameras(self) -> Dict:
        """Get all enabled cameras"""
        return {k: v for k, v in self.cameras.items() if v.get("enabled", False)}
    
    def test_camera_connection(self, camera_id: str) -> bool:
        """Test if camera can be connected"""
        if camera_id not in self.cameras:
            return False
        
        camera_config = self.cameras[camera_id]
        source = camera_config["source"]
        
        try:
            cap = cv2.VideoCapture(source)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                return ret
            return False
        except Exception as e:
            logger.error(f"Error testing camera {camera_id}: {e}")
            return False
    
    def get_camera_info(self, camera_id: str) -> Optional[Dict]:
        """Get camera configuration"""
        return self.cameras.get(camera_id)
    
    def list_cameras(self) -> List[str]:
        """List all camera IDs"""
        return list(self.cameras.keys())
    
    def enable_camera(self, camera_id: str):
        """Enable a camera"""
        if camera_id in self.cameras:
            self.cameras[camera_id]["enabled"] = True
            self.save_camera_config()
    
    def disable_camera(self, camera_id: str):
        """Disable a camera"""
        if camera_id in self.cameras:
            self.cameras[camera_id]["enabled"] = False
            self.save_camera_config()


def detect_available_cameras() -> List[int]:
    """Detect available camera devices"""
    available_cameras = []
    
    # Test camera indices 0-10
    for i in range(10):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()
        except:
            continue
    
    return available_cameras


def main():
    """Test camera manager"""
    print("🎥 Camera Manager Test")
    print("=" * 30)
    
    # Create camera manager
    manager = CameraManager()
    
    # Detect available cameras
    available = detect_available_cameras()
    print(f"📹 Available cameras: {available}")
    
    # List configured cameras
    cameras = manager.list_cameras()
    print(f"⚙️ Configured cameras: {cameras}")
    
    # Test camera connections
    for camera_id in cameras:
        connected = manager.test_camera_connection(camera_id)
        status = "✅ Connected" if connected else "❌ Not available"
        camera_info = manager.get_camera_info(camera_id)
        print(f"  {camera_id}: {status} - {camera_info['name']}")
    
    # Show enabled cameras
    enabled = manager.get_enabled_cameras()
    print(f"🟢 Enabled cameras: {list(enabled.keys())}")


if __name__ == "__main__":
    main()

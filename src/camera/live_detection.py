"""
Live Camera Feed Integration for Emergency Detection
Captures real-time video and runs AI predictions
"""
import cv2
import numpy as np
import threading
import time
import requests
import base64
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveCameraDetector:
    """Real-time camera feed processor for emergency detection"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.api_base_url = api_base_url
        self.cameras = {}
        self.detection_threads = {}
        self.running = False
        
        # Detection settings
        self.detection_interval = 2.0  # seconds between detections
        self.frame_skip = 30  # process every Nth frame for performance
        self.confidence_threshold = 0.7
        
        # Emergency callbacks
        self.emergency_callbacks = []
        
    def add_camera(self, camera_id: str, source, location: Dict[str, float] = None):
        """
        Add a camera source for monitoring
        
        Args:
            camera_id: Unique identifier for the camera
            source: Camera source (0 for webcam, URL for IP camera, file path for video)
            location: Camera location coordinates {"x": float, "y": float}
        """
        self.cameras[camera_id] = {
            "source": source,
            "location": location or {"x": 0.0, "y": 0.0},
            "cap": None,
            "last_detection": None,
            "frame_count": 0
        }
        logger.info(f"Added camera {camera_id} with source: {source}")
    
    def add_emergency_callback(self, callback: Callable):
        """Add callback function to be called when emergency is detected"""
        self.emergency_callbacks.append(callback)
    
    def start_monitoring(self):
        """Start monitoring all cameras"""
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        logger.info("Starting live camera monitoring...")
        
        # Initialize camera connections
        for camera_id, camera_info in self.cameras.items():
            try:
                cap = cv2.VideoCapture(camera_info["source"])
                if cap.isOpened():
                    camera_info["cap"] = cap
                    # Start detection thread for this camera
                    thread = threading.Thread(
                        target=self._detection_loop,
                        args=(camera_id,),
                        daemon=True
                    )
                    thread.start()
                    self.detection_threads[camera_id] = thread
                    logger.info(f"Started monitoring camera {camera_id}")
                else:
                    logger.error(f"Failed to open camera {camera_id}")
            except Exception as e:
                logger.error(f"Error initializing camera {camera_id}: {e}")
    
    def stop_monitoring(self):
        """Stop monitoring all cameras"""
        logger.info("Stopping camera monitoring...")
        self.running = False
        
        # Close all camera connections
        for camera_id, camera_info in self.cameras.items():
            if camera_info["cap"]:
                camera_info["cap"].release()
                camera_info["cap"] = None
        
        # Wait for threads to finish
        for thread in self.detection_threads.values():
            thread.join(timeout=5.0)
        
        self.detection_threads.clear()
        cv2.destroyAllWindows()
        logger.info("Camera monitoring stopped")
    
    def _detection_loop(self, camera_id: str):
        """Main detection loop for a camera"""
        camera_info = self.cameras[camera_id]
        cap = camera_info["cap"]
        
        logger.info(f"Detection loop started for camera {camera_id}")
        
        while self.running and cap and cap.isOpened():
            try:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from camera {camera_id}")
                    time.sleep(1.0)
                    continue
                
                camera_info["frame_count"] += 1
                
                # Skip frames for performance
                if camera_info["frame_count"] % self.frame_skip != 0:
                    continue
                
                # Run detections on this frame
                self._process_frame(camera_id, frame)
                
                # Wait before next detection
                time.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in detection loop for camera {camera_id}: {e}")
                time.sleep(1.0)
    
    def _process_frame(self, camera_id: str, frame: np.ndarray):
        """Process a single frame for emergency detection"""
        try:
            # Resize frame for faster processing
            height, width = frame.shape[:2]
            if width > 640:
                scale = 640 / width
                new_width = 640
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert frame to base64 for API
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            camera_info = self.cameras[camera_id]
            
            # Run fire detection
            self._detect_fire(camera_id, frame_base64, camera_info["location"])
            
            # Run crowd analysis
            self._analyze_crowd(camera_id, frame_base64, camera_info["location"])
            
            # Update last detection time
            camera_info["last_detection"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Error processing frame from camera {camera_id}: {e}")
    
    def _detect_fire(self, camera_id: str, frame_base64: str, location: Dict[str, float]):
        """Run fire detection on frame"""
        try:
            response = requests.post(
                f"{self.api_base_url}/emergencies/detect/fire",
                json={
                    "image": frame_base64,
                    "camera_id": camera_id,
                    "location": location
                },
                timeout=5.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("fire_detected") and result.get("confidence", 0) > self.confidence_threshold:
                    logger.warning(f"🔥 FIRE DETECTED by camera {camera_id}! Confidence: {result['confidence']:.2f}")
                    self._handle_emergency("fire", camera_id, result)
                else:
                    logger.debug(f"No fire detected by camera {camera_id}")
            else:
                logger.error(f"Fire detection API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in fire detection for camera {camera_id}: {e}")
    
    def _analyze_crowd(self, camera_id: str, frame_base64: str, location: Dict[str, float]):
        """Run crowd analysis on frame"""
        try:
            response = requests.post(
                f"{self.api_base_url}/emergencies/analyze/crowd",
                json={
                    "image": frame_base64,
                    "camera_id": camera_id,
                    "area_sqm": 100.0  # Default area, should be configured per camera
                },
                timeout=5.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                density_level = result.get("density_level", "low")
                if density_level in ["high", "critical"]:
                    logger.warning(f"👥 HIGH CROWD DENSITY detected by camera {camera_id}! Level: {density_level}")
                    self._handle_emergency("crowd", camera_id, result)
                else:
                    logger.debug(f"Normal crowd density at camera {camera_id}: {density_level}")
            else:
                logger.error(f"Crowd analysis API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error in crowd analysis for camera {camera_id}: {e}")
    
    def _handle_emergency(self, emergency_type: str, camera_id: str, detection_result: Dict):
        """Handle detected emergency"""
        emergency_data = {
            "type": emergency_type,
            "camera_id": camera_id,
            "detection_result": detection_result,
            "timestamp": datetime.now().isoformat(),
            "location": self.cameras[camera_id]["location"]
        }
        
        # Call all registered callbacks
        for callback in self.emergency_callbacks:
            try:
                callback(emergency_data)
            except Exception as e:
                logger.error(f"Error in emergency callback: {e}")
        
        # Log emergency
        logger.critical(f"🚨 EMERGENCY DETECTED: {emergency_type.upper()} at camera {camera_id}")
    
    def get_camera_status(self) -> Dict:
        """Get status of all cameras"""
        status = {}
        for camera_id, camera_info in self.cameras.items():
            status[camera_id] = {
                "connected": camera_info["cap"] is not None and camera_info["cap"].isOpened(),
                "frames_processed": camera_info["frame_count"],
                "last_detection": camera_info["last_detection"].isoformat() if camera_info["last_detection"] else None,
                "location": camera_info["location"]
            }
        return status
    
    def capture_snapshot(self, camera_id: str) -> Optional[np.ndarray]:
        """Capture a single frame from camera"""
        if camera_id not in self.cameras:
            return None
        
        cap = self.cameras[camera_id]["cap"]
        if cap and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                return frame
        return None


def emergency_alert_callback(emergency_data: Dict):
    """Example emergency callback function"""
    print(f"\n🚨 EMERGENCY ALERT 🚨")
    print(f"Type: {emergency_data['type'].upper()}")
    print(f"Camera: {emergency_data['camera_id']}")
    print(f"Time: {emergency_data['timestamp']}")
    print(f"Location: {emergency_data['location']}")
    
    if emergency_data['type'] == 'fire':
        result = emergency_data['detection_result']
        print(f"Fire Confidence: {result.get('confidence', 0):.2f}")
        if result.get('emergency_id'):
            print(f"Emergency ID: {result['emergency_id']}")
    
    elif emergency_data['type'] == 'crowd':
        result = emergency_data['detection_result']
        print(f"People Count: {result.get('people_count', 0)}")
        print(f"Density Level: {result.get('density_level', 'unknown')}")
    
    print("-" * 50)


def main():
    """Example usage of live camera detection"""
    print("🎥 Live Camera Emergency Detection System")
    print("=" * 50)
    
    # Create detector
    detector = LiveCameraDetector()
    
    # Add emergency callback
    detector.add_emergency_callback(emergency_alert_callback)
    
    # Add cameras (modify these sources for your setup)
    detector.add_camera("webcam", 0, {"x": 100.0, "y": 200.0})  # Default webcam
    # detector.add_camera("ip_cam_1", "http://192.168.1.100:8080/video", {"x": 300.0, "y": 400.0})  # IP camera
    # detector.add_camera("video_file", "test_video.mp4", {"x": 500.0, "y": 600.0})  # Video file
    
    try:
        # Start monitoring
        detector.start_monitoring()
        
        print("📹 Camera monitoring started!")
        print("🔥 Watching for fires...")
        print("👥 Monitoring crowd density...")
        print("Press Ctrl+C to stop")
        
        # Keep running and show status
        while True:
            time.sleep(10)
            status = detector.get_camera_status()
            print(f"\n📊 Camera Status: {datetime.now().strftime('%H:%M:%S')}")
            for camera_id, info in status.items():
                connected = "✅" if info["connected"] else "❌"
                print(f"  {camera_id}: {connected} Frames: {info['frames_processed']}")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping camera monitoring...")
    finally:
        detector.stop_monitoring()
        print("✅ Camera monitoring stopped")


if __name__ == "__main__":
    main()

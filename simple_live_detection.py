"""
Simple Live Camera Emergency Detection
Real-time fire and crowd detection from webcam with accurate fire detection
"""
import cv2
import numpy as np
import requests
import base64
import time
import threading
from datetime import datetime
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())
from src.models.accurate_fire_detector import AccurateFireDetector

class SimpleLiveDetector:
    """Simple live emergency detection from webcam"""
    
    def __init__(self, camera_index=0, api_url="http://127.0.0.1:8000/api/v1"):
        self.camera_index = camera_index
        self.api_url = api_url
        self.running = False
        self.cap = None

        # Detection settings
        self.detection_interval = 3.0  # seconds between API calls
        self.last_detection = 0

        # Statistics
        self.frames_processed = 0
        self.emergencies_detected = 0
        self.start_time = None

        # Analytics data
        self.fire_detections = 0
        self.crowd_alerts = 0
        self.behavior_alerts = 0
        self.last_fire_confidence = 0.0
        self.last_crowd_count = 0
        self.last_behavior_threat = 0.0

        # Initialize accurate fire detector
        self.fire_detector = AccurateFireDetector()
        print("✅ Accurate fire detector initialized")
    
    def start(self):
        """Start live detection"""
        print("🎥 Starting Simple Live Emergency Detection")
        print("=" * 50)
        
        # Check API server
        if not self._check_api():
            print("❌ API server not running. Start it with: python run_server.py")
            return False
        
        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"❌ Cannot open camera {self.camera_index}")
            return False
        
        print(f"✅ Camera {self.camera_index} opened successfully")
        
        # Get camera info
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"📐 Resolution: {width}x{height}, FPS: {fps}")
        
        self.running = True
        self.start_time = datetime.now()
        
        print("\n🚀 Live detection started!")
        print("🔥 Watching for fires...")
        print("👥 Monitoring crowd density...")
        print("📺 Camera feed will show detection results")
        print("Press 'q' to quit, 's' for screenshot")
        print("-" * 50)
        
        try:
            self._detection_loop()
        except KeyboardInterrupt:
            print("\n🛑 Stopping detection...")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop detection"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        if self.start_time:
            duration = datetime.now() - self.start_time
            print(f"\n📊 Session Summary:")
            print(f"⏱️ Duration: {str(duration).split('.')[0]}")
            print(f"🎬 Frames processed: {self.frames_processed}")
            print(f"🚨 Emergencies detected: {self.emergencies_detected}")
        
        print("✅ Live detection stopped")
    
    def _check_api(self):
        """Check if API server is running"""
        try:
            response = requests.get(f"http://127.0.0.1:8000/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def _detection_loop(self):
        """Main detection loop"""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            self.frames_processed += 1
            
            # Run detection every few seconds
            current_time = time.time()
            if current_time - self.last_detection >= self.detection_interval:
                self.last_detection = current_time
                
                # Run detection in background thread to avoid blocking
                detection_thread = threading.Thread(
                    target=self._run_detection,
                    args=(frame.copy(),),
                    daemon=True
                )
                detection_thread.start()
            
            # Accurate fire detection
            fire_result = self.fire_detector.detect_fire(frame)
            fire_detected = fire_result.get("fire_detected", False)
            fire_confidence = fire_result.get("confidence", 0.0)

            # Update analytics
            self.last_fire_confidence = fire_confidence
            if fire_detected:
                self.fire_detections += 1
                print(f"🔥 FIRE DETECTED! Confidence: {fire_confidence:.3f} (Detection #{self.fire_detections})")
            
            # Clean camera feed - no overlays for professional look
            # Only add minimal status indicator
            self._add_minimal_status(frame, fire_detected)

            # Show clean camera feed
            cv2.imshow('Emergency Monitoring Camera', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self._save_screenshot(frame)
    

    
    def _add_minimal_status(self, frame, fire_detected):
        """Add minimal status indicator to camera feed"""
        # Small status indicator in corner
        height, width = frame.shape[:2]

        # Status circle in top-right corner
        center = (width - 30, 30)
        color = (0, 0, 255) if fire_detected else (0, 255, 0)  # Red if fire, Green if safe
        cv2.circle(frame, center, 15, color, -1)
        cv2.circle(frame, center, 15, (255, 255, 255), 2)

        # Small text
        status_text = "ALERT" if fire_detected else "SAFE"
        cv2.putText(frame, status_text, (width - 60, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (10, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _run_detection(self, frame):
        """Run API detection on frame"""
        try:
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Fire detection
            self._detect_fire_api(frame_base64)
            
            # Crowd analysis
            self._detect_crowd_api(frame_base64)
            
        except Exception as e:
            print(f"Error in API detection: {e}")
    
    def _detect_fire_api(self, frame_base64):
        """Call fire detection API with real camera data"""
        try:
            response = requests.post(
                f"{self.api_url}/emergencies/detect/fire",
                json={
                    "image": frame_base64,
                    "camera_id": f"webcam_{self.camera_index}",
                    "location": {"x": 100.0, "y": 200.0},
                    "use_real_detection": True  # Flag to use real detection
                },
                timeout=5.0
            )

            if response.status_code == 200:
                result = response.json()
                fire_detected = result.get("fire_detected", False)
                confidence = result.get("confidence", 0)

                # Update local analytics
                self.last_fire_confidence = confidence

                if fire_detected:
                    self.fire_detections += 1
                    print(f"🔥 FIRE DETECTED BY API! Confidence: {confidence:.3f}")
                    print(f"   Detection methods: {result.get('method_details', {})}")
                    if result.get("emergency_id"):
                        print(f"🚨 Emergency created: ID {result['emergency_id']}")
                        self.emergencies_detected += 1
                else:
                    # Only print occasionally to avoid spam
                    if self.frames_processed % 90 == 0:  # Every ~3 seconds at 30fps
                        print(f"🔍 Fire check: Confidence {confidence:.3f} (Safe)")

        except Exception as e:
            print(f"Fire detection API error: {e}")
    
    def _detect_crowd_api(self, frame_base64):
        """Call crowd analysis API with real camera data"""
        try:
            response = requests.post(
                f"{self.api_url}/emergencies/analyze/crowd",
                json={
                    "image": frame_base64,
                    "area_sqm": 50.0,
                    "camera_id": f"webcam_{self.camera_index}",
                    "use_real_detection": True  # Flag to use real detection
                },
                timeout=5.0
            )

            if response.status_code == 200:
                result = response.json()
                density_level = result.get("density_level", "low")
                people_count = result.get("people_count", 0)
                density_per_sqm = result.get("density_per_sqm", 0.0)

                # Update local analytics
                self.last_crowd_count = people_count

                if density_level in ["high", "critical"]:
                    self.crowd_alerts += 1
                    print(f"👥 HIGH CROWD DENSITY! Level: {density_level}")
                    print(f"   People: {people_count}, Density: {density_per_sqm:.1f}/m²")
                    if result.get("emergency_id"):
                        print(f"🚨 Emergency created: ID {result['emergency_id']}")
                        self.emergencies_detected += 1
                else:
                    # Periodic updates for normal crowd levels
                    if self.frames_processed % 90 == 0:
                        print(f"👥 Crowd check: {people_count} people, {density_level} density")

        except Exception as e:
            print(f"Crowd analysis API error: {e}")
    
    def _save_screenshot(self, frame):
        """Save screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detection_screenshot_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Screenshot saved: {filename}")


def main():
    """Main function"""
    print("🎥 Simple Live Emergency Detection System")
    print("🚨 Real-time AI-powered emergency detection from webcam")
    print("=" * 60)
    
    # Create and start detector
    detector = SimpleLiveDetector(camera_index=0)
    
    print("🔗 Make sure your API server is running:")
    print("   python run_server.py")
    print("   API: http://127.0.0.1:8000")
    print()
    
    # Start detection
    detector.start()


if __name__ == "__main__":
    main()

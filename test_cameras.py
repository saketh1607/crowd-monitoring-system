"""
Test camera availability and basic functionality
"""
import cv2
import numpy as np
import time
from datetime import datetime

def test_camera_availability():
    """Test which cameras are available"""
    print("🎥 Testing Camera Availability")
    print("=" * 40)
    
    available_cameras = []
    
    # Test camera indices 0-5
    for i in range(6):
        print(f"Testing camera {i}...", end=" ")
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"✅ Available ({width}x{height})")
                    available_cameras.append(i)
                else:
                    print("❌ Cannot read frames")
                cap.release()
            else:
                print("❌ Cannot open")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📹 Available cameras: {available_cameras}")
    return available_cameras

def test_camera_capture(camera_index=0):
    """Test capturing frames from a camera"""
    print(f"\n🎬 Testing Camera {camera_index} Capture")
    print("=" * 40)
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Cannot open camera {camera_index}")
            return False
        
        print("✅ Camera opened successfully")
        
        # Get camera properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"📐 Resolution: {width}x{height}")
        print(f"🎞️ FPS: {fps}")
        
        # Capture a few frames
        print("\n📸 Capturing test frames...")
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"  Frame {i+1}: ✅ {frame.shape}")
            else:
                print(f"  Frame {i+1}: ❌ Failed to capture")
            time.sleep(0.5)
        
        cap.release()
        print("✅ Camera test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing camera: {e}")
        return False

def test_fire_detection_colors(camera_index=0):
    """Test simple fire detection using color analysis"""
    print(f"\n🔥 Testing Fire Detection on Camera {camera_index}")
    print("=" * 40)
    print("Hold something red/orange/yellow in front of the camera to test fire detection")
    print("Press 'q' to quit, 's' to take snapshot")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Cannot open camera {camera_index}")
            return
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to capture frame")
                break
            
            frame_count += 1
            
            # Simple fire detection using color
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Fire color ranges (red, orange, yellow)
            lower_fire1 = np.array([0, 50, 50])
            upper_fire1 = np.array([10, 255, 255])
            lower_fire2 = np.array([170, 50, 50])
            upper_fire2 = np.array([180, 255, 255])
            
            mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
            mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
            fire_mask = cv2.bitwise_or(mask1, mask2)
            
            # Calculate fire percentage
            fire_pixels = cv2.countNonZero(fire_mask)
            total_pixels = frame.shape[0] * frame.shape[1]
            fire_percentage = fire_pixels / total_pixels
            confidence = min(fire_percentage * 10, 1.0)
            
            # Add detection info to frame
            cv2.putText(frame, f"Fire Detection Test", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if confidence > 0.1:
                cv2.putText(frame, "🔥 FIRE DETECTED!", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                print(f"🔥 Fire detected! Confidence: {confidence:.2f}")
            
            # Show frame
            cv2.imshow('Fire Detection Test', frame)
            cv2.imshow('Fire Mask', fire_mask)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"snapshot_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Snapshot saved: {filename}")
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"✅ Processed {frame_count} frames")
        
    except Exception as e:
        print(f"❌ Error in fire detection test: {e}")

def main():
    """Main test function"""
    print("🎥 Camera System Test")
    print("🚨 Emergency Detection Camera Testing")
    print("=" * 50)
    
    # Test camera availability
    available_cameras = test_camera_availability()
    
    if not available_cameras:
        print("\n❌ No cameras detected!")
        print("\n📝 Troubleshooting:")
        print("  1. Connect a webcam or USB camera")
        print("  2. Check camera permissions")
        print("  3. Close other applications using the camera")
        print("  4. Try different USB ports")
        return
    
    # Test the first available camera
    camera_index = available_cameras[0]
    
    # Test basic capture
    if test_camera_capture(camera_index):
        print(f"\n🎬 Camera {camera_index} is working!")
        
        # Ask user if they want to test fire detection
        response = input(f"\n🔥 Test fire detection with camera {camera_index}? (y/n): ")
        if response.lower() == 'y':
            test_fire_detection_colors(camera_index)
    
    print("\n✅ Camera testing completed!")
    print("\n🚀 Next steps:")
    print("  1. Run: python live_camera_server.py")
    print("  2. Make sure your API server is running: python run_server.py")
    print("  3. Watch for real-time emergency detection!")

if __name__ == "__main__":
    main()

"""
Accurate Fire Detection System
Combines multiple detection methods for higher accuracy
"""
import cv2
import numpy as np
import tensorflow as tf
import joblib
import os
from datetime import datetime
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class AccurateFireDetector:
    """Advanced fire detection with multiple validation methods"""
    
    def __init__(self, model_path: str = "data/models/fire_detection_model.h5"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.model_loaded = False
        
        # Detection thresholds (more conservative)
        self.color_threshold = 0.15  # Increased from 0.1
        self.motion_threshold = 0.3
        self.combined_threshold = 0.6  # Require higher confidence
        
        # Fire characteristics
        self.fire_colors = {
            'red_lower1': np.array([0, 120, 70]),    # More restrictive
            'red_upper1': np.array([10, 255, 255]),
            'red_lower2': np.array([170, 120, 70]),  # More restrictive
            'red_upper2': np.array([180, 255, 255]),
            'orange_lower': np.array([10, 120, 70]), # More restrictive
            'orange_upper': np.array([25, 255, 255])
        }
        
        # Previous frame for motion detection
        self.prev_frame = None
        self.frame_count = 0
        
        # Load models
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models if available"""
        try:
            # Try to load the trained fire detection model
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"Loaded trained fire detection model: {self.model_path}")
                
                # Try to load scaler
                scaler_path = "data/models/fire_scaler.pkl"
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                    logger.info("Loaded fire detection scaler")
                
                self.model_loaded = True
            else:
                logger.warning(f"Trained model not found: {self.model_path}")
                logger.info("Using advanced color-based detection")
                
        except Exception as e:
            logger.error(f"Error loading fire detection model: {e}")
            logger.info("Falling back to advanced color-based detection")
    
    def detect_fire(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive fire detection using multiple methods
        
        Args:
            frame: Input video frame
            
        Returns:
            Detection result with confidence and details
        """
        self.frame_count += 1
        
        try:
            # Method 1: Advanced color analysis
            color_result = self._detect_fire_by_color(frame)
            
            # Method 2: Motion analysis (fire flickers)
            motion_result = self._detect_fire_by_motion(frame)
            
            # Method 3: ML model prediction (if available)
            ml_result = self._detect_fire_by_ml(frame)
            
            # Method 4: Texture analysis
            texture_result = self._detect_fire_by_texture(frame)
            
            # Combine all methods for final decision
            final_result = self._combine_detections(
                color_result, motion_result, ml_result, texture_result, frame
            )
            
            # Store current frame for next motion analysis
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in fire detection: {e}")
            return {
                "fire_detected": False,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _detect_fire_by_color(self, frame: np.ndarray) -> Dict[str, float]:
        """Advanced color-based fire detection"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create masks for fire colors with stricter thresholds
            red_mask1 = cv2.inRange(hsv, self.fire_colors['red_lower1'], self.fire_colors['red_upper1'])
            red_mask2 = cv2.inRange(hsv, self.fire_colors['red_lower2'], self.fire_colors['red_upper2'])
            orange_mask = cv2.inRange(hsv, self.fire_colors['orange_lower'], self.fire_colors['orange_upper'])
            
            # Combine masks
            fire_mask = cv2.bitwise_or(red_mask1, red_mask2)
            fire_mask = cv2.bitwise_or(fire_mask, orange_mask)
            
            # Apply morphological operations to reduce noise
            kernel = np.ones((3, 3), np.uint8)
            fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
            fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel)
            
            # Calculate fire percentage
            fire_pixels = cv2.countNonZero(fire_mask)
            total_pixels = frame.shape[0] * frame.shape[1]
            fire_percentage = fire_pixels / total_pixels
            
            # Additional validation: check if fire regions are connected
            contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter small contours (noise)
            min_area = 100  # Minimum area for fire region
            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            
            # Calculate confidence based on area and shape
            confidence = 0.0
            if valid_contours:
                total_fire_area = sum(cv2.contourArea(c) for c in valid_contours)
                confidence = min(total_fire_area / (frame.shape[0] * frame.shape[1]) * 5, 1.0)
            
            return {
                "method": "color",
                "confidence": confidence,
                "fire_percentage": fire_percentage,
                "contour_count": len(valid_contours)
            }
            
        except Exception as e:
            logger.error(f"Error in color-based detection: {e}")
            return {"method": "color", "confidence": 0.0, "error": str(e)}
    
    def _detect_fire_by_motion(self, frame: np.ndarray) -> Dict[str, float]:
        """Detect fire by motion patterns (flickering)"""
        try:
            if self.prev_frame is None:
                return {"method": "motion", "confidence": 0.0}
            
            # Convert current frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference
            diff = cv2.absdiff(self.prev_frame, gray)
            
            # Threshold the difference
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            
            # Calculate motion intensity
            motion_pixels = cv2.countNonZero(thresh)
            total_pixels = frame.shape[0] * frame.shape[1]
            motion_ratio = motion_pixels / total_pixels
            
            # Fire typically has moderate motion (not too much, not too little)
            if 0.05 < motion_ratio < 0.3:  # Optimal range for fire motion
                confidence = min(motion_ratio * 3, 1.0)
            else:
                confidence = 0.0
            
            return {
                "method": "motion",
                "confidence": confidence,
                "motion_ratio": motion_ratio
            }
            
        except Exception as e:
            logger.error(f"Error in motion-based detection: {e}")
            return {"method": "motion", "confidence": 0.0, "error": str(e)}
    
    def _detect_fire_by_texture(self, frame: np.ndarray) -> Dict[str, float]:
        """Detect fire by texture analysis"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate local binary pattern (simplified)
            # Fire has irregular, chaotic texture patterns
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Calculate texture variance
            texture_variance = np.var(gradient_magnitude)
            
            # Fire typically has high texture variance
            # Normalize to 0-1 range
            confidence = min(texture_variance / 1000, 1.0)
            
            return {
                "method": "texture",
                "confidence": confidence,
                "texture_variance": texture_variance
            }
            
        except Exception as e:
            logger.error(f"Error in texture-based detection: {e}")
            return {"method": "texture", "confidence": 0.0, "error": str(e)}
    
    def _detect_fire_by_ml(self, frame: np.ndarray) -> Dict[str, float]:
        """Use trained ML model for fire detection"""
        try:
            if not self.model_loaded or self.model is None:
                return {"method": "ml", "confidence": 0.0, "note": "Model not available"}
            
            # Preprocess frame for ML model
            processed_frame = self._preprocess_for_ml(frame)
            
            # Make prediction
            prediction = self.model.predict(processed_frame, verbose=0)[0][0]
            
            return {
                "method": "ml",
                "confidence": float(prediction),
                "model_used": True
            }
            
        except Exception as e:
            logger.error(f"Error in ML-based detection: {e}")
            return {"method": "ml", "confidence": 0.0, "error": str(e)}
    
    def _preprocess_for_ml(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for ML model"""
        try:
            # Resize to model input size (assuming 224x224)
            resized = cv2.resize(frame, (224, 224))
            
            # Normalize pixel values
            normalized = resized.astype(np.float32) / 255.0
            
            # Add batch dimension
            batch = np.expand_dims(normalized, axis=0)
            
            return batch
            
        except Exception as e:
            logger.error(f"Error preprocessing frame: {e}")
            return np.zeros((1, 224, 224, 3))
    
    def _combine_detections(self, color_result: Dict, motion_result: Dict, 
                          ml_result: Dict, texture_result: Dict, frame: np.ndarray) -> Dict[str, Any]:
        """Combine all detection methods for final decision"""
        try:
            # Extract confidences
            color_conf = color_result.get("confidence", 0.0)
            motion_conf = motion_result.get("confidence", 0.0)
            ml_conf = ml_result.get("confidence", 0.0)
            texture_conf = texture_result.get("confidence", 0.0)
            
            # Weighted combination (ML model gets highest weight if available)
            if self.model_loaded and ml_conf > 0:
                # Use ML model as primary with other methods as validation
                weights = {"ml": 0.5, "color": 0.2, "motion": 0.2, "texture": 0.1}
                combined_confidence = (
                    ml_conf * weights["ml"] +
                    color_conf * weights["color"] +
                    motion_conf * weights["motion"] +
                    texture_conf * weights["texture"]
                )
            else:
                # Use traditional methods with equal weighting
                weights = {"color": 0.4, "motion": 0.3, "texture": 0.3}
                combined_confidence = (
                    color_conf * weights["color"] +
                    motion_conf * weights["motion"] +
                    texture_conf * weights["texture"]
                )
            
            # Additional validation: require multiple methods to agree
            detection_count = sum([
                color_conf > self.color_threshold,
                motion_conf > self.motion_threshold,
                ml_conf > 0.5 if self.model_loaded else False,
                texture_conf > 0.3
            ])
            
            # Require at least 2 methods to agree for fire detection
            fire_detected = combined_confidence > self.combined_threshold and detection_count >= 2
            
            # Additional false positive reduction
            if fire_detected:
                # Check if the detected region is reasonable for fire
                if color_result.get("contour_count", 0) == 0:
                    fire_detected = False
                    combined_confidence *= 0.5
            
            return {
                "fire_detected": fire_detected,
                "confidence": float(combined_confidence),
                "method_details": {
                    "color": color_result,
                    "motion": motion_result,
                    "ml": ml_result,
                    "texture": texture_result
                },
                "detection_count": detection_count,
                "weights_used": weights,
                "timestamp": datetime.utcnow().isoformat(),
                "frame_number": self.frame_count
            }
            
        except Exception as e:
            logger.error(f"Error combining detections: {e}")
            return {
                "fire_detected": False,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


def test_fire_detector():
    """Test the accurate fire detector"""
    print("🔥 Testing Accurate Fire Detector")
    print("=" * 40)
    
    detector = AccurateFireDetector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("📹 Camera opened. Testing fire detection...")
    print("🔥 Hold red/orange objects to test")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run detection
        result = detector.detect_fire(frame)
        
        # Display results
        fire_detected = result.get("fire_detected", False)
        confidence = result.get("confidence", 0.0)
        
        # Add overlay
        color = (0, 0, 255) if fire_detected else (0, 255, 0)
        status = "FIRE DETECTED!" if fire_detected else "No Fire"
        
        cv2.putText(frame, f"Status: {status}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Confidence: {confidence:.3f}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show method details
        if "method_details" in result:
            details = result["method_details"]
            y_pos = 110
            for method, data in details.items():
                method_conf = data.get("confidence", 0.0)
                cv2.putText(frame, f"{method}: {method_conf:.3f}", (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
        
        cv2.imshow('Accurate Fire Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_fire_detector()

"""
Emergency Detection ML Models
"""
import numpy as np
import cv2
import torch
import torch.nn as nn
import tensorflow as tf
from typing import Dict, List, Tuple, Optional, Any
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FireDetectionModel:
    """Computer vision model for fire detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.confidence_threshold = 0.7
        self.model_path = model_path
        self._model_loaded = False
    
    def load_model(self):
        """Load pre-trained fire detection model"""
        if self._model_loaded:
            return

        try:
            if self.model_path and os.path.exists(self.model_path):
                # Load custom trained model
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"Fire detection model loaded from {self.model_path}")
            else:
                # Use a simple CNN for demonstration
                self.model = self._create_simple_cnn()
                logger.info("Fire detection model created (simple CNN)")
            self._model_loaded = True
        except Exception as e:
            logger.error(f"Error loading fire detection model: {e}")
            self.model = self._create_simple_cnn()
            self._model_loaded = True
    
    def _create_simple_cnn(self):
        """Create a simple CNN for fire detection"""
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for fire detection"""
        # Resize image
        image = cv2.resize(image, (224, 224))
        # Normalize pixel values
        image = image.astype(np.float32) / 255.0
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        return image
    
    def detect_fire(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect fire in image"""
        try:
            # Load model if not already loaded
            if not self._model_loaded:
                self.load_model()

            if self.model is None:
                # Fallback to simple color-based detection for demo
                return self._simple_fire_detection(image)

            processed_image = self.preprocess_image(image)
            prediction = self.model.predict(processed_image)[0][0]
            
            is_fire = prediction > self.confidence_threshold
            
            return {
                "fire_detected": bool(is_fire),
                "confidence": float(prediction),
                "timestamp": datetime.utcnow().isoformat(),
                "threshold": self.confidence_threshold
            }
        except Exception as e:
            logger.error(f"Error in fire detection: {e}")
            return {
                "fire_detected": False,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _simple_fire_detection(self, image: np.ndarray) -> Dict[str, Any]:
        """Simple color-based fire detection for demo purposes"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # Define fire color ranges (red, orange, yellow)
            lower_fire1 = np.array([0, 50, 50])
            upper_fire1 = np.array([10, 255, 255])
            lower_fire2 = np.array([170, 50, 50])
            upper_fire2 = np.array([180, 255, 255])

            # Create masks for fire colors
            mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
            mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
            fire_mask = cv2.bitwise_or(mask1, mask2)

            # Calculate fire percentage
            fire_pixels = cv2.countNonZero(fire_mask)
            total_pixels = image.shape[0] * image.shape[1]
            fire_percentage = fire_pixels / total_pixels

            # Determine if fire is detected
            confidence = min(fire_percentage * 10, 1.0)  # Scale to 0-1
            fire_detected = confidence > 0.1

            return {
                "fire_detected": fire_detected,
                "confidence": float(confidence),
                "fire_percentage": float(fire_percentage),
                "method": "color_based_detection",
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in simple fire detection: {e}")
            return {
                "fire_detected": False,
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class CrowdDensityAnalyzer:
    """Analyze crowd density from camera feeds"""
    
    def __init__(self):
        self.person_detector = cv2.HOGDescriptor()
        self.person_detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.density_thresholds = {
            "low": 1.0,
            "medium": 2.5,
            "high": 4.0,
            "critical": 6.0
        }
    
    def detect_people(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect people in image using HOG descriptor"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect people
            boxes, weights = self.person_detector.detectMultiScale(
                gray, 
                winStride=(8, 8),
                padding=(32, 32),
                scale=1.05
            )
            
            return boxes.tolist()
        except Exception as e:
            logger.error(f"Error in people detection: {e}")
            return []
    
    def calculate_density(self, image: np.ndarray, area_sqm: float = 100.0) -> Dict[str, Any]:
        """Calculate crowd density per square meter"""
        try:
            people_boxes = self.detect_people(image)
            people_count = len(people_boxes)
            density = people_count / area_sqm
            
            # Determine density level
            density_level = "low"
            for level, threshold in self.density_thresholds.items():
                if density >= threshold:
                    density_level = level
            
            return {
                "people_count": people_count,
                "density_per_sqm": density,
                "density_level": density_level,
                "area_sqm": area_sqm,
                "people_boxes": people_boxes,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calculating crowd density: {e}")
            return {
                "people_count": 0,
                "density_per_sqm": 0.0,
                "density_level": "unknown",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class BehaviorAnalyzer:
    """Analyze crowd behavior for security threats"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.behavior_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def extract_features(self, motion_data: np.ndarray, audio_data: np.ndarray) -> np.ndarray:
        """Extract behavioral features from motion and audio data"""
        features = []
        
        # Motion features
        if motion_data.size > 0:
            features.extend([
                np.mean(motion_data),
                np.std(motion_data),
                np.max(motion_data),
                np.min(motion_data),
                np.percentile(motion_data, 95)
            ])
        else:
            features.extend([0, 0, 0, 0, 0])
        
        # Audio features
        if audio_data.size > 0:
            features.extend([
                np.mean(audio_data),
                np.std(audio_data),
                np.max(audio_data),
                np.min(audio_data),
                np.percentile(audio_data, 95)
            ])
        else:
            features.extend([0, 0, 0, 0, 0])
        
        return np.array(features)
    
    def train_models(self, training_data: List[Dict[str, Any]]):
        """Train behavior analysis models"""
        try:
            features = []
            labels = []
            
            for sample in training_data:
                feature_vector = self.extract_features(
                    sample.get('motion_data', np.array([])),
                    sample.get('audio_data', np.array([]))
                )
                features.append(feature_vector)
                labels.append(sample.get('label', 'normal'))
            
            features = np.array(features)
            
            # Train scaler
            features_scaled = self.scaler.fit_transform(features)
            
            # Train anomaly detector
            self.anomaly_detector.fit(features_scaled)
            
            # Train behavior classifier
            self.behavior_classifier.fit(features_scaled, labels)
            
            self.is_trained = True
            logger.info("Behavior analysis models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training behavior models: {e}")
    
    def analyze_behavior(self, motion_data: np.ndarray, audio_data: np.ndarray) -> Dict[str, Any]:
        """Analyze behavior for potential security threats"""
        try:
            if not self.is_trained:
                return {
                    "threat_detected": False,
                    "confidence": 0.0,
                    "behavior_type": "unknown",
                    "error": "Models not trained",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            features = self.extract_features(motion_data, audio_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Anomaly detection
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
            
            # Behavior classification
            behavior_proba = self.behavior_classifier.predict_proba(features_scaled)[0]
            behavior_classes = self.behavior_classifier.classes_
            behavior_type = behavior_classes[np.argmax(behavior_proba)]
            behavior_confidence = np.max(behavior_proba)
            
            # Determine threat level
            threat_detected = is_anomaly or (behavior_type in ['aggressive', 'suspicious'] and behavior_confidence > 0.7)
            
            return {
                "threat_detected": threat_detected,
                "confidence": float(behavior_confidence),
                "behavior_type": behavior_type,
                "anomaly_score": float(anomaly_score),
                "is_anomaly": is_anomaly,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in behavior analysis: {e}")
            return {
                "threat_detected": False,
                "confidence": 0.0,
                "behavior_type": "unknown",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


class SensorAnomalyDetector:
    """Detect anomalies in sensor data"""
    
    def __init__(self):
        self.detectors = {}
        self.scalers = {}
        self.thresholds = {
            'temperature': {'min': -10, 'max': 50},
            'smoke': {'min': 0, 'max': 100},
            'sound': {'min': 0, 'max': 120},
            'motion': {'min': 0, 'max': 1000}
        }
    
    def train_detector(self, sensor_type: str, historical_data: np.ndarray):
        """Train anomaly detector for specific sensor type"""
        try:
            # Initialize scaler and detector
            scaler = StandardScaler()
            detector = IsolationForest(contamination=0.1, random_state=42)
            
            # Prepare data
            data_scaled = scaler.fit_transform(historical_data.reshape(-1, 1))
            
            # Train detector
            detector.fit(data_scaled)
            
            # Store models
            self.scalers[sensor_type] = scaler
            self.detectors[sensor_type] = detector
            
            logger.info(f"Anomaly detector trained for {sensor_type}")
            
        except Exception as e:
            logger.error(f"Error training anomaly detector for {sensor_type}: {e}")
    
    def detect_anomaly(self, sensor_type: str, value: float) -> Dict[str, Any]:
        """Detect if sensor reading is anomalous"""
        try:
            # Check basic thresholds
            threshold_violation = False
            if sensor_type in self.thresholds:
                thresh = self.thresholds[sensor_type]
                threshold_violation = value < thresh['min'] or value > thresh['max']
            
            # ML-based anomaly detection
            ml_anomaly = False
            anomaly_score = 0.0
            
            if sensor_type in self.detectors:
                scaler = self.scalers[sensor_type]
                detector = self.detectors[sensor_type]
                
                value_scaled = scaler.transform([[value]])
                anomaly_score = detector.decision_function(value_scaled)[0]
                ml_anomaly = detector.predict(value_scaled)[0] == -1
            
            is_anomaly = threshold_violation or ml_anomaly
            
            return {
                "is_anomaly": is_anomaly,
                "threshold_violation": threshold_violation,
                "ml_anomaly": ml_anomaly,
                "anomaly_score": float(anomaly_score),
                "sensor_type": sensor_type,
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomaly for {sensor_type}: {e}")
            return {
                "is_anomaly": False,
                "error": str(e),
                "sensor_type": sensor_type,
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }

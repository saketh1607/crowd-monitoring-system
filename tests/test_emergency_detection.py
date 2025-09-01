"""
Tests for emergency detection models
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import tempfile
import os

from src.models.emergency_detector import (
    FireDetectionModel,
    CrowdDensityAnalyzer,
    BehaviorAnalyzer,
    SensorAnomalyDetector
)


class TestFireDetectionModel:
    """Test fire detection functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fire_detector = FireDetectionModel()
    
    def test_model_initialization(self):
        """Test model initializes correctly"""
        assert self.fire_detector.model is not None
        assert self.fire_detector.confidence_threshold == 0.7
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        processed = self.fire_detector.preprocess_image(test_image)
        
        assert processed.shape == (1, 224, 224, 3)
        assert processed.dtype == np.float32
        assert np.all(processed >= 0) and np.all(processed <= 1)
    
    def test_detect_fire_normal_image(self):
        """Test fire detection on normal image"""
        # Create normal image (mostly blue/green)
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :, 1] = 100  # Green channel
        test_image[:, :, 2] = 150  # Blue channel
        
        result = self.fire_detector.detect_fire(test_image)
        
        assert isinstance(result, dict)
        assert 'fire_detected' in result
        assert 'confidence' in result
        assert 'timestamp' in result
        assert isinstance(result['fire_detected'], bool)
        assert 0 <= result['confidence'] <= 1
    
    def test_detect_fire_error_handling(self):
        """Test error handling in fire detection"""
        # Test with invalid input
        result = self.fire_detector.detect_fire(None)
        
        assert 'error' in result
        assert result['fire_detected'] is False


class TestCrowdDensityAnalyzer:
    """Test crowd density analysis"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.crowd_analyzer = CrowdDensityAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initializes correctly"""
        assert self.crowd_analyzer.person_detector is not None
        assert len(self.crowd_analyzer.density_thresholds) == 4
    
    def test_detect_people(self):
        """Test people detection"""
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        boxes = self.crowd_analyzer.detect_people(test_image)
        
        assert isinstance(boxes, list)
        # Each box should have 4 coordinates if people detected
        for box in boxes:
            assert len(box) == 4
    
    def test_calculate_density(self):
        """Test density calculation"""
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = self.crowd_analyzer.calculate_density(test_image, area_sqm=100.0)
        
        assert isinstance(result, dict)
        assert 'people_count' in result
        assert 'density_per_sqm' in result
        assert 'density_level' in result
        assert 'area_sqm' in result
        assert result['area_sqm'] == 100.0
        assert result['density_level'] in ['low', 'medium', 'high', 'critical']


class TestBehaviorAnalyzer:
    """Test behavior analysis"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.behavior_analyzer = BehaviorAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initializes correctly"""
        assert self.behavior_analyzer.scaler is not None
        assert self.behavior_analyzer.anomaly_detector is not None
        assert self.behavior_analyzer.behavior_classifier is not None
        assert not self.behavior_analyzer.is_trained
    
    def test_extract_features(self):
        """Test feature extraction"""
        motion_data = np.random.rand(100)
        audio_data = np.random.rand(100)
        
        features = self.behavior_analyzer.extract_features(motion_data, audio_data)
        
        assert isinstance(features, np.ndarray)
        assert len(features) == 10  # 5 motion + 5 audio features
    
    def test_extract_features_empty_data(self):
        """Test feature extraction with empty data"""
        motion_data = np.array([])
        audio_data = np.array([])
        
        features = self.behavior_analyzer.extract_features(motion_data, audio_data)
        
        assert isinstance(features, np.ndarray)
        assert len(features) == 10
        assert np.all(features == 0)  # Should be zeros for empty data
    
    def test_train_models(self):
        """Test model training"""
        # Create training data
        training_data = []
        for i in range(100):
            sample = {
                'motion_data': np.random.rand(50),
                'audio_data': np.random.rand(50),
                'label': 'normal' if i < 80 else 'suspicious'
            }
            training_data.append(sample)
        
        self.behavior_analyzer.train_models(training_data)
        
        assert self.behavior_analyzer.is_trained
    
    def test_analyze_behavior_untrained(self):
        """Test behavior analysis without training"""
        motion_data = np.random.rand(50)
        audio_data = np.random.rand(50)
        
        result = self.behavior_analyzer.analyze_behavior(motion_data, audio_data)
        
        assert 'error' in result
        assert result['threat_detected'] is False


class TestSensorAnomalyDetector:
    """Test sensor anomaly detection"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.anomaly_detector = SensorAnomalyDetector()
    
    def test_initialization(self):
        """Test detector initializes correctly"""
        assert isinstance(self.anomaly_detector.detectors, dict)
        assert isinstance(self.anomaly_detector.scalers, dict)
        assert isinstance(self.anomaly_detector.thresholds, dict)
        assert len(self.anomaly_detector.thresholds) == 4
    
    def test_train_detector(self):
        """Test training anomaly detector"""
        # Generate normal temperature data
        normal_data = np.random.normal(22, 2, 1000)  # Normal room temperature
        
        self.anomaly_detector.train_detector('temperature', normal_data)
        
        assert 'temperature' in self.anomaly_detector.detectors
        assert 'temperature' in self.anomaly_detector.scalers
    
    def test_detect_anomaly_threshold(self):
        """Test threshold-based anomaly detection"""
        # Test extreme temperature
        result = self.anomaly_detector.detect_anomaly('temperature', 60.0)
        
        assert isinstance(result, dict)
        assert 'is_anomaly' in result
        assert 'threshold_violation' in result
        assert 'sensor_type' in result
        assert 'value' in result
        assert result['threshold_violation'] is True  # 60°C is above threshold
        assert result['value'] == 60.0
    
    def test_detect_anomaly_normal_value(self):
        """Test normal value detection"""
        result = self.anomaly_detector.detect_anomaly('temperature', 22.0)
        
        assert result['threshold_violation'] is False  # 22°C is normal
        assert result['value'] == 22.0
    
    def test_detect_anomaly_with_ml(self):
        """Test ML-based anomaly detection"""
        # Train detector first
        normal_data = np.random.normal(22, 2, 1000)
        self.anomaly_detector.train_detector('temperature', normal_data)
        
        # Test normal value
        result = self.anomaly_detector.detect_anomaly('temperature', 23.0)
        assert 'anomaly_score' in result
        assert 'ml_anomaly' in result
    
    def test_detect_anomaly_error_handling(self):
        """Test error handling in anomaly detection"""
        # Test with invalid sensor type
        result = self.anomaly_detector.detect_anomaly('invalid_sensor', 25.0)
        
        # Should still work but without ML detection
        assert 'is_anomaly' in result
        assert result['sensor_type'] == 'invalid_sensor'


class TestIntegration:
    """Integration tests for emergency detection system"""
    
    def test_fire_and_crowd_integration(self):
        """Test fire detection and crowd analysis together"""
        fire_detector = FireDetectionModel()
        crowd_analyzer = CrowdDensityAnalyzer()
        
        # Create test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Run both analyses
        fire_result = fire_detector.detect_fire(test_image)
        crowd_result = crowd_analyzer.calculate_density(test_image)
        
        # Both should return valid results
        assert 'fire_detected' in fire_result
        assert 'people_count' in crowd_result
        
        # Simulate emergency scenario
        if fire_result['fire_detected'] and crowd_result['people_count'] > 50:
            emergency_level = 'critical'
        elif fire_result['fire_detected'] or crowd_result['density_level'] == 'high':
            emergency_level = 'high'
        else:
            emergency_level = 'low'
        
        assert emergency_level in ['low', 'high', 'critical']
    
    def test_sensor_behavior_integration(self):
        """Test sensor and behavior analysis integration"""
        sensor_detector = SensorAnomalyDetector()
        behavior_analyzer = BehaviorAnalyzer()
        
        # Train behavior analyzer
        training_data = []
        for i in range(50):
            sample = {
                'motion_data': np.random.rand(30),
                'audio_data': np.random.rand(30),
                'label': 'normal' if i < 40 else 'suspicious'
            }
            training_data.append(sample)
        
        behavior_analyzer.train_models(training_data)
        
        # Test sensor readings
        temp_result = sensor_detector.detect_anomaly('temperature', 45.0)  # High temp
        sound_result = sensor_detector.detect_anomaly('sound', 110.0)      # High sound
        
        # Test behavior
        motion_data = np.random.rand(30) * 100  # High motion
        audio_data = np.random.rand(30) * 120   # High audio
        behavior_result = behavior_analyzer.analyze_behavior(motion_data, audio_data)
        
        # Check if multiple anomalies indicate emergency
        anomaly_count = sum([
            temp_result['is_anomaly'],
            sound_result['is_anomaly'],
            behavior_result['threat_detected']
        ])
        
        emergency_detected = anomaly_count >= 2
        assert isinstance(emergency_detected, bool)


if __name__ == '__main__':
    pytest.main([__file__])

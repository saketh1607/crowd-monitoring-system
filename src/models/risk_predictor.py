"""
Risk Assessment and Prediction Models
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, classification_report
import joblib
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EventRiskPredictor:
    """Predict risk levels for events based on various factors"""
    
    def __init__(self):
        self.risk_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        self.feature_names = [
            'attendance', 'duration_hours', 'venue_capacity_ratio',
            'weather_temp', 'weather_humidity', 'weather_wind_speed',
            'historical_incidents', 'security_personnel_ratio',
            'medical_personnel_ratio', 'time_of_day', 'day_of_week'
        ]
    
    def prepare_features(self, event_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for risk prediction"""
        features = []
        
        # Event characteristics
        features.append(event_data.get('attendance', 0))
        
        # Duration in hours
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')
        if start_time and end_time:
            duration = (end_time - start_time).total_seconds() / 3600
        else:
            duration = 8  # default 8 hours
        features.append(duration)
        
        # Venue capacity ratio
        attendance = event_data.get('attendance', 0)
        venue_capacity = event_data.get('venue_capacity', 1000)
        capacity_ratio = attendance / venue_capacity if venue_capacity > 0 else 0
        features.append(capacity_ratio)
        
        # Weather conditions
        weather = event_data.get('weather_conditions', {})
        features.append(weather.get('temperature', 20))
        features.append(weather.get('humidity', 50))
        features.append(weather.get('wind_speed', 5))
        
        # Historical data
        features.append(event_data.get('historical_incidents', 0))
        
        # Personnel ratios
        security_count = event_data.get('security_personnel', 10)
        medical_count = event_data.get('medical_personnel', 5)
        features.append(security_count / attendance if attendance > 0 else 0)
        features.append(medical_count / attendance if attendance > 0 else 0)
        
        # Time factors
        if start_time:
            features.append(start_time.hour)
            features.append(start_time.weekday())
        else:
            features.append(12)  # noon
            features.append(5)   # Saturday
        
        return np.array(features)
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the risk prediction model"""
        try:
            features = []
            targets = []
            
            for event in training_data:
                feature_vector = self.prepare_features(event)
                features.append(feature_vector)
                targets.append(event.get('risk_score', 0.5))  # 0-1 scale
            
            features = np.array(features)
            targets = np.array(targets)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train model
            self.risk_model.fit(features_scaled, targets)
            
            self.is_trained = True
            logger.info("Risk prediction model trained successfully")
            
            # Calculate feature importance
            importance = self.risk_model.feature_importances_
            for i, feature in enumerate(self.feature_names):
                logger.info(f"Feature importance - {feature}: {importance[i]:.3f}")
                
        except Exception as e:
            logger.error(f"Error training risk prediction model: {e}")
    
    def predict_risk(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict risk level for an event"""
        try:
            if not self.is_trained:
                return {
                    "risk_score": 0.5,
                    "risk_level": "medium",
                    "confidence": 0.0,
                    "error": "Model not trained",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            features = self.prepare_features(event_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            risk_score = self.risk_model.predict(features_scaled)[0]
            risk_score = max(0, min(1, risk_score))  # Clamp to [0, 1]
            
            # Determine risk level
            if risk_score < 0.3:
                risk_level = "low"
            elif risk_score < 0.6:
                risk_level = "medium"
            elif risk_score < 0.8:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # Calculate confidence (simplified)
            confidence = 1.0 - abs(risk_score - 0.5) * 2
            
            return {
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "confidence": float(confidence),
                "factors": self._analyze_risk_factors(features),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            return {
                "risk_score": 0.5,
                "risk_level": "medium",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _analyze_risk_factors(self, features: np.ndarray) -> Dict[str, str]:
        """Analyze which factors contribute most to risk"""
        factors = {}
        
        # Attendance factor
        attendance = features[0]
        if attendance > 10000:
            factors["attendance"] = "high"
        elif attendance > 5000:
            factors["attendance"] = "medium"
        else:
            factors["attendance"] = "low"
        
        # Capacity ratio
        capacity_ratio = features[2]
        if capacity_ratio > 0.9:
            factors["capacity"] = "overcrowded"
        elif capacity_ratio > 0.7:
            factors["capacity"] = "high"
        else:
            factors["capacity"] = "normal"
        
        # Weather
        temp = features[3]
        if temp > 35 or temp < 0:
            factors["weather"] = "extreme"
        elif temp > 30 or temp < 5:
            factors["weather"] = "challenging"
        else:
            factors["weather"] = "favorable"
        
        return factors


class IncidentPredictor:
    """Predict likelihood of specific incident types"""
    
    def __init__(self):
        self.medical_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.fire_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.security_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_incident_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for incident prediction"""
        features = []
        
        # Current conditions
        features.append(data.get('crowd_density', 0))
        features.append(data.get('noise_level', 0))
        features.append(data.get('temperature', 20))
        features.append(data.get('humidity', 50))
        
        # Event characteristics
        features.append(data.get('event_type_encoded', 0))
        features.append(data.get('time_since_start', 0))
        features.append(data.get('alcohol_served', 0))
        
        # Historical patterns
        features.append(data.get('incidents_last_hour', 0))
        features.append(data.get('similar_events_incidents', 0))
        
        # Resource availability
        features.append(data.get('medical_response_time', 300))
        features.append(data.get('security_coverage', 0.5))
        
        return np.array(features)
    
    def train_models(self, training_data: List[Dict[str, Any]]):
        """Train incident prediction models"""
        try:
            features = []
            medical_labels = []
            fire_labels = []
            security_labels = []
            
            for sample in training_data:
                feature_vector = self.prepare_incident_features(sample)
                features.append(feature_vector)
                
                medical_labels.append(sample.get('medical_incident', 0))
                fire_labels.append(sample.get('fire_incident', 0))
                security_labels.append(sample.get('security_incident', 0))
            
            features = np.array(features)
            features_scaled = self.scaler.fit_transform(features)
            
            # Train models
            self.medical_model.fit(features_scaled, medical_labels)
            self.fire_model.fit(features_scaled, fire_labels)
            self.security_model.fit(features_scaled, security_labels)
            
            self.is_trained = True
            logger.info("Incident prediction models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training incident prediction models: {e}")
    
    def predict_incidents(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict likelihood of different incident types"""
        try:
            if not self.is_trained:
                return {
                    "medical_risk": 0.1,
                    "fire_risk": 0.05,
                    "security_risk": 0.1,
                    "overall_risk": 0.1,
                    "error": "Models not trained",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            features = self.prepare_incident_features(current_data)
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Get predictions
            medical_prob = self.medical_model.predict_proba(features_scaled)[0][1]
            fire_prob = self.fire_model.predict_proba(features_scaled)[0][1]
            security_prob = self.security_model.predict_proba(features_scaled)[0][1]
            
            # Calculate overall risk
            overall_risk = max(medical_prob, fire_prob, security_prob)
            
            return {
                "medical_risk": float(medical_prob),
                "fire_risk": float(fire_prob),
                "security_risk": float(security_prob),
                "overall_risk": float(overall_risk),
                "recommendations": self._generate_recommendations(
                    medical_prob, fire_prob, security_prob
                ),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting incidents: {e}")
            return {
                "medical_risk": 0.1,
                "fire_risk": 0.05,
                "security_risk": 0.1,
                "overall_risk": 0.1,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _generate_recommendations(self, medical_risk: float, fire_risk: float, 
                                security_risk: float) -> List[str]:
        """Generate recommendations based on risk levels"""
        recommendations = []
        
        if medical_risk > 0.7:
            recommendations.append("Increase medical personnel on standby")
            recommendations.append("Prepare additional ambulances")
        
        if fire_risk > 0.7:
            recommendations.append("Increase fire safety patrols")
            recommendations.append("Check fire suppression systems")
        
        if security_risk > 0.7:
            recommendations.append("Deploy additional security personnel")
            recommendations.append("Increase surveillance monitoring")
        
        if max(medical_risk, fire_risk, security_risk) > 0.8:
            recommendations.append("Consider crowd control measures")
            recommendations.append("Alert emergency services")
        
        return recommendations


class WeatherImpactAnalyzer:
    """Analyze weather impact on event safety"""
    
    def __init__(self):
        self.weather_thresholds = {
            'temperature': {'extreme_low': -5, 'low': 5, 'high': 35, 'extreme_high': 40},
            'wind_speed': {'moderate': 15, 'high': 25, 'extreme': 35},
            'precipitation': {'light': 2, 'moderate': 10, 'heavy': 25},
            'humidity': {'low': 20, 'high': 80, 'extreme': 95}
        }
    
    def analyze_weather_risk(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather-related risks"""
        try:
            risks = {}
            overall_risk = 0.0
            recommendations = []
            
            # Temperature analysis
            temp = weather_data.get('temperature', 20)
            temp_risk = self._analyze_temperature_risk(temp)
            risks['temperature'] = temp_risk
            overall_risk = max(overall_risk, temp_risk['risk_score'])
            recommendations.extend(temp_risk['recommendations'])
            
            # Wind analysis
            wind_speed = weather_data.get('wind_speed', 0)
            wind_risk = self._analyze_wind_risk(wind_speed)
            risks['wind'] = wind_risk
            overall_risk = max(overall_risk, wind_risk['risk_score'])
            recommendations.extend(wind_risk['recommendations'])
            
            # Precipitation analysis
            precipitation = weather_data.get('precipitation', 0)
            precip_risk = self._analyze_precipitation_risk(precipitation)
            risks['precipitation'] = precip_risk
            overall_risk = max(overall_risk, precip_risk['risk_score'])
            recommendations.extend(precip_risk['recommendations'])
            
            return {
                "overall_weather_risk": overall_risk,
                "risk_breakdown": risks,
                "recommendations": list(set(recommendations)),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weather risk: {e}")
            return {
                "overall_weather_risk": 0.0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _analyze_temperature_risk(self, temperature: float) -> Dict[str, Any]:
        """Analyze temperature-related risks"""
        thresholds = self.weather_thresholds['temperature']
        
        if temperature <= thresholds['extreme_low'] or temperature >= thresholds['extreme_high']:
            risk_score = 0.9
            level = "extreme"
            recommendations = ["Consider event cancellation", "Provide emergency heating/cooling"]
        elif temperature <= thresholds['low'] or temperature >= thresholds['high']:
            risk_score = 0.6
            level = "high"
            recommendations = ["Increase medical personnel", "Provide warming/cooling stations"]
        else:
            risk_score = 0.1
            level = "low"
            recommendations = []
        
        return {
            "risk_score": risk_score,
            "level": level,
            "value": temperature,
            "recommendations": recommendations
        }
    
    def _analyze_wind_risk(self, wind_speed: float) -> Dict[str, Any]:
        """Analyze wind-related risks"""
        thresholds = self.weather_thresholds['wind_speed']
        
        if wind_speed >= thresholds['extreme']:
            risk_score = 0.9
            level = "extreme"
            recommendations = ["Secure all temporary structures", "Consider event postponement"]
        elif wind_speed >= thresholds['high']:
            risk_score = 0.6
            level = "high"
            recommendations = ["Check stage and tent security", "Monitor structures closely"]
        elif wind_speed >= thresholds['moderate']:
            risk_score = 0.3
            level = "moderate"
            recommendations = ["Secure loose items", "Monitor weather updates"]
        else:
            risk_score = 0.1
            level = "low"
            recommendations = []
        
        return {
            "risk_score": risk_score,
            "level": level,
            "value": wind_speed,
            "recommendations": recommendations
        }
    
    def _analyze_precipitation_risk(self, precipitation: float) -> Dict[str, Any]:
        """Analyze precipitation-related risks"""
        thresholds = self.weather_thresholds['precipitation']
        
        if precipitation >= thresholds['heavy']:
            risk_score = 0.8
            level = "high"
            recommendations = ["Prepare drainage systems", "Consider indoor alternatives"]
        elif precipitation >= thresholds['moderate']:
            risk_score = 0.5
            level = "moderate"
            recommendations = ["Provide covered areas", "Monitor ground conditions"]
        elif precipitation >= thresholds['light']:
            risk_score = 0.2
            level = "low"
            recommendations = ["Have umbrellas/ponchos available"]
        else:
            risk_score = 0.0
            level = "none"
            recommendations = []
        
        return {
            "risk_score": risk_score,
            "level": level,
            "value": precipitation,
            "recommendations": recommendations
        }

"""
Create mock models for testing the emergency management system
Run this if you haven't downloaded the real models from Colab yet
"""
import os
import numpy as np
import joblib
import json
from datetime import datetime

# Ensure models directory exists
os.makedirs('data/models', exist_ok=True)

def create_mock_tensorflow_model():
    """Create a mock TensorFlow model file"""
    try:
        import tensorflow as tf
        from tensorflow.keras import models, layers
        
        # Create simple models
        fire_model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(6,)),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        fire_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        fire_model.save('data/models/fire_detection_model.h5')
        print("✅ Created fire_detection_model.h5")
        
        crowd_model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(5,)),
            layers.Dense(32, activation='relu'),
            layers.Dense(4, activation='softmax')
        ])
        crowd_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        crowd_model.save('data/models/crowd_density_model.h5')
        print("✅ Created crowd_density_model.h5")
        
        return True
    except ImportError:
        print("⚠️ TensorFlow not available, skipping TensorFlow models")
        return False

def create_mock_sklearn_models():
    """Create mock scikit-learn models"""
    try:
        from sklearn.ensemble import RandomForestClassifier, IsolationForest
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        
        # Behavior analysis model
        behavior_model = RandomForestClassifier(n_estimators=10, random_state=42)
        # Train on dummy data
        X_dummy = np.random.rand(100, 5)
        y_dummy = np.random.choice(['normal', 'suspicious', 'aggressive', 'panic'], 100)
        
        # Label encoder
        behavior_encoder = LabelEncoder()
        y_encoded = behavior_encoder.fit_transform(y_dummy)
        
        # Scaler
        behavior_scaler = StandardScaler()
        X_scaled = behavior_scaler.fit_transform(X_dummy)
        
        # Train model
        behavior_model.fit(X_scaled, y_encoded)
        
        # Save models
        joblib.dump(behavior_model, 'data/models/behavior_analysis_model.pkl')
        joblib.dump(behavior_encoder, 'data/models/behavior_label_encoder.pkl')
        joblib.dump(behavior_scaler, 'data/models/behavior_scaler.pkl')
        print("✅ Created behavior analysis models")
        
        # Create scalers for fire and crowd models
        fire_scaler = StandardScaler()
        fire_scaler.fit(np.random.rand(100, 6))
        joblib.dump(fire_scaler, 'data/models/fire_scaler.pkl')
        print("✅ Created fire_scaler.pkl")
        
        crowd_scaler = StandardScaler()
        crowd_scaler.fit(np.random.rand(100, 5))
        joblib.dump(crowd_scaler, 'data/models/crowd_scaler.pkl')
        print("✅ Created crowd_scaler.pkl")
        
        # Create sensor anomaly models
        sensor_types = ['temperature', 'humidity', 'sound', 'motion']
        for sensor_type in sensor_types:
            # Anomaly detector
            anomaly_model = IsolationForest(contamination=0.1, random_state=42)
            anomaly_model.fit(np.random.rand(100, 1))
            joblib.dump(anomaly_model, f'data/models/{sensor_type}_anomaly_model.pkl')
            
            # Scaler
            scaler = StandardScaler()
            scaler.fit(np.random.rand(100, 1))
            joblib.dump(scaler, f'data/models/{sensor_type}_scaler.pkl')
            
            print(f"✅ Created {sensor_type} anomaly models")
        
        return True
    except ImportError as e:
        print(f"⚠️ Scikit-learn not available: {e}")
        return False

def create_model_summary():
    """Create model summary file"""
    summary = {
        "training_date": datetime.now().isoformat(),
        "model_type": "mock_models_for_testing",
        "models": {
            "fire_detection": {
                "type": "neural_network",
                "accuracy": 0.85,
                "file": "fire_detection_model.h5",
                "scaler": "fire_scaler.pkl"
            },
            "crowd_density": {
                "type": "neural_network", 
                "accuracy": 0.82,
                "file": "crowd_density_model.h5",
                "scaler": "crowd_scaler.pkl"
            },
            "behavior_analysis": {
                "type": "random_forest",
                "accuracy": 0.78,
                "files": [
                    "behavior_analysis_model.pkl",
                    "behavior_label_encoder.pkl", 
                    "behavior_scaler.pkl"
                ]
            },
            "anomaly_detection": {
                "type": "isolation_forest",
                "sensor_types": ["temperature", "humidity", "sound", "motion"],
                "files": [
                    "temperature_anomaly_model.pkl", "temperature_scaler.pkl",
                    "humidity_anomaly_model.pkl", "humidity_scaler.pkl", 
                    "sound_anomaly_model.pkl", "sound_scaler.pkl",
                    "motion_anomaly_model.pkl", "motion_scaler.pkl"
                ]
            }
        },
        "note": "These are mock models for testing. Replace with real trained models from Google Colab."
    }
    
    with open('data/models/model_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Created model_summary.json")

def main():
    """Create all mock models"""
    print("🔧 Creating mock models for testing...")
    print("=" * 50)
    
    # Create TensorFlow models
    tf_success = create_mock_tensorflow_model()
    
    # Create scikit-learn models
    sklearn_success = create_mock_sklearn_models()
    
    # Create summary
    create_model_summary()
    
    print("\n" + "=" * 50)
    if tf_success and sklearn_success:
        print("🎉 All mock models created successfully!")
        print("\n📁 Files created in data/models/:")
        
        # List created files
        model_files = os.listdir('data/models')
        for file in sorted(model_files):
            print(f"  ✅ {file}")
        
        print("\n⚠️  IMPORTANT:")
        print("These are mock models for testing only.")
        print("Replace them with real trained models from Google Colab for production use.")
        
    else:
        print("⚠️  Some models could not be created due to missing dependencies.")
        print("Install TensorFlow and scikit-learn to create all models.")
    
    print("\n🚀 You can now test the emergency management system!")

if __name__ == "__main__":
    main()

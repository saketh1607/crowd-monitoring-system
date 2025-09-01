"""
Emergency Detection Model Training Script
Run this in Google Colab for GPU acceleration
"""

# Install required packages
import subprocess
import sys

def install_packages():
    packages = [
        'tensorflow==2.13.0',
        'scikit-learn==1.3.0', 
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'opencv-python',
        'pillow',
        'joblib'
    ]
    
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Uncomment the line below if running for the first time
# install_packages()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# TensorFlow/Keras
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models

# Scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import joblib

print("Libraries imported successfully!")
print(f"TensorFlow version: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")

def generate_fire_data(num_samples=2000):
    """Generate synthetic fire detection data"""
    data = []
    labels = []
    
    for i in range(num_samples):
        if i < num_samples // 2:
            # Fire images - higher red/orange values
            red_intensity = np.random.normal(200, 30)
            orange_intensity = np.random.normal(180, 25)
            brightness = np.random.normal(150, 20)
            motion_intensity = np.random.normal(80, 15)
            label = 1  # Fire
        else:
            # Non-fire images
            red_intensity = np.random.normal(100, 40)
            orange_intensity = np.random.normal(90, 35)
            brightness = np.random.normal(120, 30)
            motion_intensity = np.random.normal(30, 20)
            label = 0  # No fire
        
        features = [red_intensity, orange_intensity, brightness, motion_intensity,
                   np.random.normal(50, 10), np.random.normal(75, 15)]
        data.append(features)
        labels.append(label)
    
    return np.array(data), np.array(labels)

def generate_crowd_data(num_samples=2000):
    """Generate synthetic crowd density data"""
    data = []
    labels = []
    
    for i in range(num_samples):
        people_count = np.random.randint(0, 200)
        area_coverage = np.random.uniform(0.1, 0.9)
        movement_speed = np.random.uniform(0, 5)
        noise_level = np.random.uniform(40, 100)
        
        density = people_count * area_coverage / 100
        if density < 1.0:
            density_level = 0  # Low
        elif density < 2.5:
            density_level = 1  # Medium
        elif density < 4.0:
            density_level = 2  # High
        else:
            density_level = 3  # Critical
        
        features = [people_count, area_coverage, movement_speed, noise_level, density]
        data.append(features)
        labels.append(density_level)
    
    return np.array(data), np.array(labels)

def generate_behavior_data(num_samples=2000):
    """Generate synthetic behavior analysis data"""
    data = []
    labels = []
    
    behavior_types = ['normal', 'suspicious', 'aggressive', 'panic']
    
    for i in range(num_samples):
        behavior = np.random.choice(behavior_types)
        
        if behavior == 'normal':
            motion_variance = np.random.normal(10, 3)
            audio_level = np.random.normal(60, 10)
            speed_changes = np.random.normal(2, 1)
        elif behavior == 'suspicious':
            motion_variance = np.random.normal(25, 5)
            audio_level = np.random.normal(50, 8)
            speed_changes = np.random.normal(8, 2)
        elif behavior == 'aggressive':
            motion_variance = np.random.normal(40, 8)
            audio_level = np.random.normal(85, 15)
            speed_changes = np.random.normal(15, 3)
        else:  # panic
            motion_variance = np.random.normal(60, 10)
            audio_level = np.random.normal(95, 20)
            speed_changes = np.random.normal(25, 5)
        
        features = [motion_variance, audio_level, speed_changes,
                   np.random.normal(30, 10), np.random.normal(45, 12)]
        data.append(features)
        labels.append(behavior)
    
    return np.array(data), np.array(labels)

def train_fire_model(fire_data, fire_labels):
    """Train fire detection model"""
    print("🔥 Training Fire Detection Model...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        fire_data, fire_labels, test_size=0.2, random_state=42, stratify=fire_labels
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = models.Sequential([
        layers.Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
        layers.Dropout(0.3),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(32, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    history = model.fit(
        X_train_scaled, y_train,
        validation_data=(X_test_scaled, y_test),
        epochs=30, batch_size=32, verbose=1
    )
    
    predictions = (model.predict(X_test_scaled) > 0.5).astype(int)
    accuracy = accuracy_score(y_test, predictions)
    
    print(f"🔥 Fire Detection Accuracy: {accuracy:.4f}")
    
    # Save model and scaler
    model.save('/content/fire_detection_model.h5')
    joblib.dump(scaler, '/content/fire_scaler.pkl')
    
    return model, scaler, history, accuracy

def main():
    """Main training function"""
    print("🚀 Starting Emergency Detection Model Training...")
    print("=" * 50)
    
    # Generate datasets
    print("📊 Generating synthetic training data...")
    fire_data, fire_labels = generate_fire_data(2000)
    crowd_data, crowd_labels = generate_crowd_data(2000)
    behavior_data, behavior_labels = generate_behavior_data(2000)
    
    print(f"Fire detection data: {fire_data.shape}")
    print(f"Crowd analysis data: {crowd_data.shape}")
    print(f"Behavior analysis data: {behavior_data.shape}")
    print("✅ Data generation complete!")
    
    # Train fire detection model
    fire_model, fire_scaler, fire_history, fire_accuracy = train_fire_model(fire_data, fire_labels)
    
    # Train other models (add similar functions for crowd, behavior, sensors)
    # ... (truncated for brevity)
    
    print("\n" + "=" * 50)
    print("🎉 TRAINING COMPLETE!")
    print("=" * 50)
    print(f"🔥 Fire Detection Accuracy: {fire_accuracy:.4f}")
    print("\n📁 Files saved:")
    print("- fire_detection_model.h5")
    print("- fire_scaler.pkl")
    print("\n✅ Download files from Colab and place in your project's 'data/models/' directory.")

if __name__ == "__main__":
    main()

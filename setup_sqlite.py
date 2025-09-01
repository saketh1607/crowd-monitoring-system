"""
Simple SQLite database setup for Emergency Management System
"""
import sqlite3
import os
from datetime import datetime, timedelta

def create_sqlite_database():
    """Create SQLite database with all required tables"""
    
    # Remove existing database if it exists
    if os.path.exists("emergency_management.db"):
        os.remove("emergency_management.db")
        print("🗑️ Removed existing database")
    
    # Create new database
    conn = sqlite3.connect("emergency_management.db")
    cursor = conn.cursor()
    
    print("🔧 Creating SQLite database tables...")
    
    # Create Events table
    cursor.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            venue VARCHAR(255),
            start_time DATETIME,
            end_time DATETIME,
            expected_attendance INTEGER,
            risk_level VARCHAR(50) DEFAULT 'low',
            status VARCHAR(50) DEFAULT 'planned',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create Emergencies table
    cursor.execute("""
        CREATE TABLE emergencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            type VARCHAR(50) NOT NULL,
            severity VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            location_x FLOAT,
            location_y FLOAT,
            description TEXT,
            detection_source VARCHAR(100),
            confidence_score FLOAT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    """)
    
    # Create Resources table
    cursor.execute("""
        CREATE TABLE resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'available',
            location_x FLOAT,
            location_y FLOAT,
            capacity INTEGER,
            current_assignment VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create Sensors table
    cursor.execute("""
        CREATE TABLE sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(100) NOT NULL,
            location_x FLOAT,
            location_y FLOAT,
            status VARCHAR(50) DEFAULT 'active',
            last_reading DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create Sensor Readings table
    cursor.execute("""
        CREATE TABLE sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER NOT NULL,
            value FLOAT NOT NULL,
            unit VARCHAR(50),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_anomaly BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sensor_id) REFERENCES sensors (id)
        )
    """)
    
    print("✅ Database tables created successfully!")
    
    # Insert sample data
    print("📊 Inserting sample data...")
    
    # Sample event
    cursor.execute("""
        INSERT INTO events (name, description, venue, start_time, end_time, expected_attendance, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Summer Music Festival",
        "Large outdoor music festival with multiple stages",
        "Central Park",
        datetime.now().isoformat(),
        (datetime.now() + timedelta(days=3)).isoformat(),
        50000,
        "medium"
    ))
    
    event_id = cursor.lastrowid
    
    # Sample resources
    resources = [
        ("Ambulance Unit 1", "medical", "available", 100.0, 200.0, 4),
        ("Fire Truck Alpha", "fire", "available", 150.0, 250.0, 6),
        ("Security Team A", "security", "available", 200.0, 300.0, 8),
        ("Medical Station 1", "medical", "available", 300.0, 400.0, 20)
    ]
    
    for resource in resources:
        cursor.execute("""
            INSERT INTO resources (name, type, status, location_x, location_y, capacity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, resource)
    
    # Sample sensors
    sensors = [
        ("Temperature Sensor 1", "temperature", 50.0, 100.0),
        ("Smoke Detector 1", "smoke", 75.0, 125.0),
        ("Sound Monitor 1", "sound", 100.0, 150.0),
        ("Motion Detector 1", "motion", 125.0, 175.0)
    ]
    
    for sensor in sensors:
        cursor.execute("""
            INSERT INTO sensors (name, type, location_x, location_y)
            VALUES (?, ?, ?, ?)
        """, sensor)
    
    # Sample sensor readings
    import random
    sensor_ids = [1, 2, 3, 4]
    
    for sensor_id in sensor_ids:
        for i in range(10):
            value = random.uniform(20, 80)
            cursor.execute("""
                INSERT INTO sensor_readings (sensor_id, value, unit)
                VALUES (?, ?, ?)
            """, (sensor_id, value, "units"))
    
    conn.commit()
    conn.close()
    
    print("✅ Sample data inserted successfully!")
    print("🎉 SQLite database setup complete!")
    print("📁 Database file: emergency_management.db")
    
    return True

if __name__ == "__main__":
    try:
        create_sqlite_database()
        print("\n🚀 Ready to start the API server!")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        exit(1)

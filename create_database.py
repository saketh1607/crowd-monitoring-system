"""
Create database tables for the Emergency Management System
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.getcwd())

from src.data.database import engine, Base
from src.data.models import Event, Emergency, Resource, Sensor, SensorReading

def create_tables():
    """Create all database tables"""
    try:
        print("🔧 Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database tables created successfully!")
        print("📁 Database file: emergency_management.db")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Created tables:")
        for table in tables:
            print(f"  ✅ {table}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n🎉 Database setup complete!")
        print("🚀 Ready to start the API server!")
    else:
        print("\n⚠️ Database setup failed!")
        sys.exit(1)

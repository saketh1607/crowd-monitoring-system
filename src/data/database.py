"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config.settings import settings
from src.data.models import Base


# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with sample data"""
    create_tables()
    
    # Add sample data if needed
    db = SessionLocal()
    try:
        # Check if data already exists
        from src.data.models import Event
        if db.query(Event).first() is None:
            # Add sample event
            from datetime import datetime, timedelta
            sample_event = Event(
                name="Summer Music Festival",
                description="Large outdoor music festival",
                venue="Central Park",
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=3),
                expected_attendance=50000,
                risk_level="medium"
            )
            db.add(sample_event)
            db.commit()
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")

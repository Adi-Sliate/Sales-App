# backend/app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Get database URL from environment variable ONLY
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Use SQLite for local testing if no DATABASE_URL
    logger.warning("⚠️ DATABASE_URL not set, using SQLite for testing")
    DATABASE_URL = "sqlite:///./test.db"

# Create engine for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit=False, 
    future=True
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# backend/app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for local development with PostgreSQL
    DATABASE_URL = "postgresql://netlifydb_owner:npg_NcpZSY34drLX@ep-old-rain-ajgdncwm.c-3.us-east-2.db.netlify.com/netlifydb?sslmode=requireb"
   
    print("⚠️  DATABASE_URL not set, using default local PostgreSQL connection")

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

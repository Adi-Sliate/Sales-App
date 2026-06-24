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
    DATABASE_URL = "postgresql://test1_owner:npg_ERZgbWpmhj68@ep-purple-credit-a1p1imhv.ap-southeast-1.aws.neon.tech/test1?sslmode=require&channel_binding=require"
   
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

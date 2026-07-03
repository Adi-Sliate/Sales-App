# backend/app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# ============================================
# NEON POSTGRESQL CONNECTION
# ============================================

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback: Build from individual environment variables
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "greenpoint_migration")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Add SSL for Neon
    if "neon.tech" in DB_HOST:
        DATABASE_URL += "?sslmode=require"
    
    logger.warning("⚠️ DATABASE_URL not set, built from individual variables")

# Mask password for logging
masked_url = DATABASE_URL
if '@' in DATABASE_URL and '://' in DATABASE_URL:
    parts = DATABASE_URL.split('@')
    if ':' in parts[0]:
        user_pass = parts[0].split('://')[1] if '://' in parts[0] else parts[0]
        if ':' in user_pass:
            user = user_pass.split(':')[0]
            masked_url = parts[0].replace(user_pass, f"{user}:****") + '@' + parts[1]

logger.info(f"📡 Connecting to: {masked_url}")

# Create engine for PostgreSQL
try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    logger.info("✅ Database engine created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    raise

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

def test_connection():
    """Test the database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Database connection successful: {version[:50]}...")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

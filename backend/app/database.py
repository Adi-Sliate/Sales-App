# backend/app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

load_dotenv()

# ============================================
# DATABASE CONNECTION (Neon PostgreSQL)
# ============================================

# Your Neon database connection string
# Using your actual Neon database from the migrate.py script
NEON_USER = os.getenv("NEON_USER", "neondb_owner")
NEON_PASSWORD = os.getenv("NEON_PASSWORD", "npg_RJqr5v8zGAfS")
NEON_HOST = os.getenv("NEON_HOST", "ep-tiny-voice-atx66bw1.c-9.us-east-1.aws.neon.tech")
NEON_PORT = os.getenv("NEON_PORT", "5432")
NEON_DATABASE = os.getenv("NEON_DATABASE", "neondb")

# Build Neon connection string
NEON_URL = f"postgresql://{NEON_USER}:{quote_plus(NEON_PASSWORD)}@{NEON_HOST}:{NEON_PORT}/{NEON_DATABASE}?sslmode=require"

# Get database URL from environment variable or use Neon as default
DATABASE_URL = os.getenv("DATABASE_URL", NEON_URL)

# If DATABASE_URL is provided in env, use it
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    logger.info("📡 Using DATABASE_URL from environment")

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

# ============================================
# CREATE DATABASE ENGINE
# ============================================

try:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        future=True,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10
        }
    )
    logger.info("✅ Database engine created successfully")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    raise

# ============================================
# SESSION MAKER
# ============================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

# ============================================
# BASE CLASS FOR MODELS
# ============================================

class Base(DeclarativeBase):
    pass

# ============================================
# DATABASE DEPENDENCY
# ============================================

def get_db():
    """Get database session for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# CONNECTION TEST
# ============================================

def test_connection():
    """Test the database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Database connection successful: {version[:50]}...")
            
            # Get current database name
            db_result = conn.execute(text("SELECT current_database()"))
            db_name = db_result.fetchone()[0]
            logger.info(f"📊 Connected to database: {db_name}")
            
            # Check if TransactionMain exists
            try:
                table_check = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'TransactionMain'
                    )
                """))
                exists = table_check.fetchone()[0]
                if exists:
                    # Get count
                    count_result = conn.execute(text("SELECT COUNT(*) FROM \"TransactionMain\""))
                    count = count_result.fetchone()[0]
                    logger.info(f"📊 TransactionMain: {count:,} rows")
                else:
                    logger.warning("⚠️ TransactionMain table not found")
            except Exception as e:
                logger.warning(f"⚠️ Could not check TransactionMain: {e}")
            
            # Check if TransactionSub exists
            try:
                table_check = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'TransactionSub'
                    )
                """))
                exists = table_check.fetchone()[0]
                if exists:
                    # Get count
                    count_result = conn.execute(text("SELECT COUNT(*) FROM \"TransactionSub\""))
                    count = count_result.fetchone()[0]
                    logger.info(f"📊 TransactionSub: {count:,} rows")
                else:
                    logger.warning("⚠️ TransactionSub table not found")
            except Exception as e:
                logger.warning(f"⚠️ Could not check TransactionSub: {e}")
            
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_table_count(table_name: str):
    """Get row count for a specific table"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            return result.fetchone()[0]
    except Exception as e:
        logger.error(f"Error getting count for {table_name}: {e}")
        return None

def list_tables():
    """List all tables in the database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            return [row[0] for row in result]
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return []

def check_table_exists(table_name: str):
    """Check if a table exists"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                )
            """), {"table_name": table_name})
            return result.fetchone()[0]
    except Exception as e:
        logger.error(f"Error checking table {table_name}: {e}")
        return False

# ============================================
# RUN CONNECTION TEST ON IMPORT
# ============================================

# Uncomment to test connection when imported
# if test_connection():
#     logger.info("✅ Database is ready")
# else:
#     logger.error("❌ Database connection failed")

logger.info("✅ Database module initialized")

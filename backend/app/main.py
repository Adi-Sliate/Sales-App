# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .routers import reports
from .database import engine, Base
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sales Report API", version="1.0.0")

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reports.router)

# Serve frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        with open(index_path, "r") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Sales Report API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Sales Report API"}

@app.get("/api/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to query one record
        result = db.query(TransactionMain).first()
        return {
            "status": "connected",
            "message": "Database connection successful",
            "sample_data": result is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

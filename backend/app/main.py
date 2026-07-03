# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path
import logging

# Import your modules
from .routers import reports
from .database import engine, Base, get_db
from .models import TransactionMain

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

# Include routers with /api prefix
app.include_router(reports.router, prefix="/api")

# Serve frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    # Mount CSS and JS directories
    css_path = frontend_path / "css"
    if css_path.exists():
        app.mount("/css", StaticFiles(directory=str(css_path)), name="css")
        logger.info(f"Serving CSS from: {css_path}")
    
    js_path = frontend_path / "js"
    if js_path.exists():
        app.mount("/js", StaticFiles(directory=str(js_path)), name="js")
        logger.info(f"Serving JS from: {js_path}")

@app.get("/")
async def root():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    return {"message": "Sales Report API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Sales Report API", "version": "1.0.0"}

@app.get("/api/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to query one record
        result = db.query(TransactionMain).first()
        return {
            "status": "connected",
            "message": "Database connection successful",
            "sample_data": result is not None,
            "has_data": result is not None
        }
    except Exception as e:
        logger.error(f"Database test error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Sales Report API",
        "version": "1.0.0",
        "endpoints": [
            "/api/health",
            "/api/test-db",
            "/api/reports/sales",
            "/api/reports/sales/summary",
            "/api/reports/items",
            "/api/reports/stock/value"
        ]
    }

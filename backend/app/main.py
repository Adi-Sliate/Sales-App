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

# ============================================
# CORS - Updated with ALL frontend URLs
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://salesapp-o1rbn7lh.b4a.run",  # ✅ Your NEW frontend URL (current)
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Option A: Keep the prefix /api but add /reports to the path
# The full path will be: /api/reports/sales-summary
app.include_router(reports.router, prefix="/api")

# Option B: Add a second router without the /reports prefix
# This makes both /api/sales-summary AND /api/reports/sales-summary work
# Import the same router but without the /reports prefix
from .routers.reports import router as reports_router_no_prefix
# Create a copy of the router without the prefix
# We'll just include it with a different prefix
app.include_router(reports.router, prefix="/api")  # This gives /api/reports/...

# Option C: If you want the routes directly at /api/ without /reports
# You need to modify the reports.py file (see below)

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
    """Root endpoint - serves the frontend if available"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    return {"message": "Sales Summary Report API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sales Report API",
        "version": "1.0.0",
        "database": "Neon PostgreSQL"
    }

@app.get("/api/test-db")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT COUNT(*) FROM \"TransactionMain\""))
        count = result.fetchone()[0]
        return {
            "status": "connected",
            "message": "Database connection successful",
            "table_count": count,
            "has_data": count > 0
        }
    except Exception as e:
        logger.error(f"Database test error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/routes")
async def list_routes():
    """List all available routes for debugging"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return {
        "total_routes": len(routes),
        "routes": routes
    }

@app.get("/api")
async def api_root():
    """API root endpoint - displays all available endpoints"""
    return {
        "message": "Sales Summary Report API",
        "version": "1.0.0",
        "database": "Neon PostgreSQL",
        "frontend_urls": [
            "https://salesapp-o1rbn7lh.b4a.run",
            "https://salesapp-e1q0ga5o.b4a.run"
        ],
        "endpoint_prefixes": {
            "with_reports": "/api/reports/sales-summary",
            "without_reports": "/api/sales-summary (currently not available)"
        },
        "note": "Visit /api/routes to see all available endpoints"
    }

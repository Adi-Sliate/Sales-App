# backend/app/main.py

from pathlib import Path
import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .routers import reports

# ----------------------------------------------------
# Logging
# ----------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------------------
# FastAPI App
# ----------------------------------------------------
app = FastAPI(
    title="Sales Report API",
    version="1.0.0"
)

# ----------------------------------------------------
# Startup
# ----------------------------------------------------
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.exception(f"Database initialization failed: {e}")

# ----------------------------------------------------
# CORS
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://salesapp-wfao4392.b4a.run", 
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Routers
# ----------------------------------------------------
# If reports.py has:
# router = APIRouter(tags=["Reports"])
#
# All routes become:
# /api/sales-summary
# /api/item-summary
# /api/quantity-report
# etc.

app.include_router(reports.router, prefix="/api")

# ----------------------------------------------------
# Static Files
# ----------------------------------------------------
frontend_path = Path(__file__).parent.parent.parent / "frontend"

if frontend_path.exists():

    css_path = frontend_path / "css"
    if css_path.exists():
        app.mount("/css", StaticFiles(directory=css_path), name="css")

    js_path = frontend_path / "js"
    if js_path.exists():
        app.mount("/js", StaticFiles(directory=js_path), name="js")

# ----------------------------------------------------
# Frontend
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root():

    index_path = frontend_path / "index.html"

    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))

    return HTMLResponse("<h2>Sales Report API is running.</h2>")

# ----------------------------------------------------
# Health Check
# ----------------------------------------------------
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Sales Report API",
        "version": app.version,
        "database": "Neon PostgreSQL",
    }

# ----------------------------------------------------
# Database Test
# ----------------------------------------------------
@app.get("/api/test-db")
async def test_db(db: Session = Depends(get_db)):

    from sqlalchemy import text

    try:
        result = db.execute(text('SELECT COUNT(*) FROM "TransactionMain"'))
        count = result.scalar()

        return {
            "status": "connected",
            "records": count,
            "has_data": count > 0,
        }

    except Exception as e:
        logger.exception(e)

        return {
            "status": "error",
            "message": str(e),
        }

# ----------------------------------------------------
# Route List
# ----------------------------------------------------
@app.get("/api/routes")
async def list_routes():

    return {
        "total_routes": len(app.routes),
        "routes": [
            {
                "path": route.path,
                "methods": list(route.methods)
            }
            for route in app.routes
            if hasattr(route, "path")
        ]
    }

# ----------------------------------------------------
# API Info
# ----------------------------------------------------
@app.get("/api")
async def api_root():

    return {
        "name": app.title,
        "version": app.version,
        "database": "Neon PostgreSQL",
        "documentation": "/docs",
        "available_reports": [
            "/api/sales-summary",
            "/api/item-summary",
            "/api/quantity-report",
            "/api/bill-report",
            "/api/gp-report",
            "/api/stock-report",
            "/api/expenses-report",
            "/api/debug-sql",
        ]
    }

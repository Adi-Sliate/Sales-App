# backend/app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .routers.reports import router as reports_router
import os
from pathlib import Path

app = FastAPI(title="Sales Summary Report API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace with your Back4App URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your existing router
app.include_router(reports_router)

# Get the absolute path to frontend directory
frontend_path = Path(__file__).parent.parent.parent / "frontend"

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/")
async def root():
    """Serve the Bootstrap frontend"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        with open(index_path, "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Sales Summary Report API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Back4App"""
    return {"status": "healthy", "service": "Sales Summary Report API"}

@app.get("/api")
async def api_root():
    return {"message": "Sales Summary Report API is running"}
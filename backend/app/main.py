# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.reports import router as reports_router

app = FastAPI(title="Sales Summary Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://salesapp-e1q0ga5o.b4a.run"],   # Added your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports_router)


@app.get("/")
def root():
    return {"message": "Sales Summary Report API is running"}

# app/main.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.pools.routes import router as pools_router

app = FastAPI(
    title="AMM Game Backend",
    version="0.4.0",
    description="Constant-product AMM playground with PostgreSQL and SQLAlchemy.",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup():
    """Attempt to create database tables on application startup.

    Do not raise on failure — in local/dev environments DB may not
    be available or may require manual setup. Log the error and
    let the app start so other non-DB endpoints remain available.
    """
    try:
        init_db()
    except Exception as e:  # pragma: no cover - operational/runtime issue
        # Avoid failing app startup due to DB connectivity issues.
        print(f"init_db() failed: {e}")

# Mount feature routers
app.include_router(pools_router, prefix="/pools", tags=["pools"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.4.0"}

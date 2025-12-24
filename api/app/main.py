# app/main.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.users.routes import router as users_router
from app.experiments.routes import router as experiments_router
from app.rounds.routes import router as rounds_router

app = FastAPI(
    title="AMM Game Backend",
    version="1.0.0",
    description="Experiment-based AMM trading platform with PostgreSQL and SQLAlchemy.",
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
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(experiments_router, prefix="/experiments", tags=["experiments"])
app.include_router(rounds_router, prefix="/rounds", tags=["rounds"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AMM Game Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "users": "/users",
            "experiments": "/experiments",
            "rounds": "/rounds",
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.4.0"}

# app/main.py

from __future__ import annotations

from fastapi import FastAPI

from app.pools.routes import router as pools_router

app = FastAPI(
    title="AMM Game Backend",
    version="0.3.0",
    description="Constant-product AMM playground with a modular architecture.",
)

# Mount feature routers
app.include_router(pools_router, prefix="/pools", tags=["pools"])

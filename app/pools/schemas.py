# app/pools/schemas.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --------- Pool models --------- #

class PoolCreate(BaseModel):
    """
    Request body for creating a new liquidity pool.
    """
    x_init: float = Field(
        ...,
        gt=0,
        description="Initial reserve of token X (must be > 0).",
    )
    y_init: float = Field(
        ...,
        gt=0,
        description="Initial reserve of token Y (must be > 0).",
    )


class PoolState(BaseModel):
    """
    Representation of a liquidity pool returned by the API.
    """
    id: UUID
    x_reserve: float
    y_reserve: float
    K: float
    price_x_in_y: float
    price_y_in_x: float
    created_at: datetime


# --------- Swap models --------- #

class SwapXForYRequest(BaseModel):
    """
    Request body for swapping X for Y.
    """
    amount_in: float = Field(
        ...,
        gt=0,
        description="Amount of X sent into the pool (must be > 0).",
    )


class SwapYForXRequest(BaseModel):
    """
    Request body for swapping Y for X.
    """
    amount_in: float = Field(
        ...,
        gt=0,
        description="Amount of Y sent into the pool (must be > 0).",
    )


class SwapXForYResponse(BaseModel):
    """
    Response body after swapping X for Y.
    """
    pool: PoolState
    amount_in: float
    amount_out: float  # amount of Y received


class SwapYForXResponse(BaseModel):
    """
    Response body after swapping Y for X.
    """
    pool: PoolState
    amount_in: float
    amount_out: float  # amount of X received

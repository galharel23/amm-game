# app/pools/schemas.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# --------- Error response --------- #

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")


# --------- Pool models --------- #

class PoolCreate(BaseModel):
    """
    Request body for creating a new liquidity pool.
    """
    currency_x_id: UUID = Field(
        ...,
        description="UUID of token X currency",
    )
    currency_y_id: UUID = Field(
        ...,
        description="UUID of token Y currency",
    )
    x_init: float = Field(
        ...,
        gt=0,
        description="Initial reserve of token X (must be > 0).",
        example=1000.0,
    )
    y_init: float = Field(
        ...,
        gt=0,
        description="Initial reserve of token Y (must be > 0).",
        example=1000.0,
    )


class PoolState(BaseModel):
    """
    Representation of a liquidity pool returned by the API.
    """
    id: UUID
    # NEW: currency metadata
    currency_x_id: UUID
    currency_y_id: UUID
    currency_x_symbol: str = Field(..., description="Symbol of currency X")
    currency_y_symbol: str = Field(..., description="Symbol of currency Y")
    currency_x_name: str = Field(..., description="Name of currency X")
    currency_y_name: str = Field(..., description="Name of currency Y")

    x_reserve: float = Field(..., description="Current reserve of token X")
    y_reserve: float = Field(..., description="Current reserve of token Y")
    K: float = Field(..., description="Constant product (x_reserve * y_reserve)")
    price_x_in_y: float = Field(..., description="Price of 1 unit of X in terms of Y")
    price_y_in_x: float = Field(..., description="Price of 1 unit of Y in terms of X")
    is_active: bool = Field(..., description="Pool active status")
    created_at: datetime

    class Config:
        from_attributes = True


class PoolListResponse(BaseModel):
    """Response for listing all pools."""
    pools: list[PoolState]
    total: int = Field(..., description="Total number of pools")


# --------- Swap models --------- #

class SwapXForYRequest(BaseModel):
    """
    Request body for swapping X for Y.
    """
    amount_in: float = Field(
        ...,
        gt=0,
        description="Amount of X sent into the pool (must be > 0).",
        example=10.5,
    )
    min_amount_out: float = Field(
        default=0.0,
        ge=0,
        description="Minimum amount of Y to receive (slippage protection). If actual output is less, swap fails.",
        example=9.0,
    )


class SwapYForXRequest(BaseModel):
    """
    Request body for swapping Y for X.
    """
    amount_in: float = Field(
        ...,
        gt=0,
        description="Amount of Y sent into the pool (must be > 0).",
        example=10.5,
    )
    min_amount_out: float = Field(
        default=0.0,
        ge=0,
        description="Minimum amount of X to receive (slippage protection). If actual output is less, swap fails.",
        example=9.0,
    )


class SwapXForYResponse(BaseModel):
    """
    Response body after swapping X for Y.
    """
    pool: PoolState
    amount_in: float = Field(..., description="Amount of X sent")
    amount_out: float = Field(..., description="Amount of Y received")
    price_execution: float = Field(..., description="Effective price (amount_out / amount_in)")


class SwapYForXResponse(BaseModel):
    """
    Response body after swapping Y for X.
    """
    pool: PoolState
    amount_in: float = Field(..., description="Amount of Y sent")
    amount_out: float = Field(..., description="Amount of X received")
    price_execution: float = Field(..., description="Effective price (amount_out / amount_in)")


# --------- Currency models --------- #

class CurrencyCreate(BaseModel):
    """Request body for creating a new currency."""
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Currency symbol (e.g., 'BTC', 'ETH'). Must be unique.",
        example="BTC",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Currency full name. Must be unique.",
        example="Bitcoin",
    )
    image_url: str | None = Field(
        None,
        max_length=500,
        description="Optional URL to currency image/logo",
        example="https://example.com/btc.png",
    )


class CurrencyState(BaseModel):
    """Representation of a currency."""
    id: UUID
    symbol: str = Field(..., description="Currency symbol (e.g., 'BTC', 'ETH')")
    name: str = Field(..., description="Currency full name")
    decimals: float = Field(..., description="Number of decimal places")
    image_url: str | None = Field(None, description="URL to currency image/logo")
    pools_count: int = Field(..., description="Number of pools this currency is part of")
    created_at: datetime

    class Config:
        from_attributes = True


class CurrencyListResponse(BaseModel):
    """Response for listing currencies."""
    currencies: list[CurrencyState]
    total: int = Field(..., description="Total number of currencies")

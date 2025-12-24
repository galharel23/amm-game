# app/rounds/schemas.py

from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

from pydantic import BaseModel, Field


# -------------------- Request Schemas -------------------- #

class RoundCreate(BaseModel):
    """Schema for creating a round."""
    experiment_id: UUID
    round_number: int = Field(..., gt=0)
    is_training_round: bool = False
    counts_for_payment: bool = False
    duration_minutes: int = Field(..., gt=0)
    currency_x_id: UUID
    currency_y_id: UUID
    external_price_x: float = Field(..., gt=0)
    external_price_y: float = Field(..., gt=0)
    initial_reserve_x: float = Field(..., gt=0)
    initial_reserve_y: float = Field(..., gt=0)


class RoundUpdate(BaseModel):
    """Schema for updating a round."""
    is_training_round: Optional[bool] = None
    counts_for_payment: Optional[bool] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    external_price_x: Optional[float] = Field(None, gt=0)
    external_price_y: Optional[float] = Field(None, gt=0)
    initial_reserve_x: Optional[float] = Field(None, gt=0)
    initial_reserve_y: Optional[float] = Field(None, gt=0)


# -------------------- Response Schemas -------------------- #

class RoundResponse(BaseModel):
    """Response schema for a round."""
    id: UUID
    experiment_id: UUID
    round_number: int
    is_training_round: bool
    counts_for_payment: bool
    duration_minutes: int
    currency_x_id: UUID
    currency_y_id: UUID
    external_price_x: Decimal
    external_price_y: Decimal
    initial_reserve_x: Decimal
    initial_reserve_y: Decimal
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ExperimentRoundResponse(BaseModel):
    """Response schema for an experiment round (pool instance)."""
    id: UUID
    round_id: UUID
    group_id: UUID
    reserve_x: Decimal
    reserve_y: Decimal
    k_constant: Decimal
    transaction_fee_percent: Decimal
    is_active: bool
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RoundListResponse(BaseModel):
    """Response for listing rounds."""
    rounds: list[RoundResponse]
    total: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str

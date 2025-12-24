# app/experiments/schemas.py

from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# -------------------- Request Schemas -------------------- #

class ExperimentCreate(BaseModel):
    """Schema for creating an experiment."""
    name: str = Field(..., min_length=1, max_length=255)
    num_rounds: int = Field(..., gt=0)
    num_training_rounds: int = Field(0, ge=0)
    num_rounds_for_payment: int = Field(..., gt=0)
    num_players: int = Field(..., gt=0)
    num_groups: int = Field(..., gt=0)


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    num_rounds: Optional[int] = Field(None, gt=0)
    num_training_rounds: Optional[int] = Field(None, ge=0)
    num_rounds_for_payment: Optional[int] = Field(None, gt=0)
    num_players: Optional[int] = Field(None, gt=0)
    num_groups: Optional[int] = Field(None, gt=0)


class GroupCreate(BaseModel):
    """Schema for creating a group."""
    experiment_id: UUID
    group_number: int = Field(..., gt=0)


# -------------------- Response Schemas -------------------- #

class GroupResponse(BaseModel):
    """Response schema for a group."""
    id: UUID
    experiment_id: UUID
    group_number: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExperimentResponse(BaseModel):
    """Response schema for an experiment."""
    id: UUID
    name: str
    num_rounds: int
    num_training_rounds: int
    num_rounds_for_payment: int
    num_players: int
    num_groups: int
    created_by_id: UUID
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ExperimentWithGroups(ExperimentResponse):
    """Response schema for experiment with groups."""
    groups: list[GroupResponse]


class ExperimentListResponse(BaseModel):
    """Response for listing experiments."""
    experiments: list[ExperimentResponse]
    total: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str

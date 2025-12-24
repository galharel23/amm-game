# app/users/schemas.py

from __future__ import annotations

from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserType


# -------------------- Request Schemas -------------------- #

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=6)
    user_type: UserType
    username: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class PlayerAssignGroup(BaseModel):
    """Schema for assigning a player to a group."""
    player_id: UUID
    group_id: UUID


# -------------------- Response Schemas -------------------- #

class UserBase(BaseModel):
    """Base user information."""
    id: UUID
    email: str
    username: Optional[str]
    user_type: UserType
    created_at: datetime

    class Config:
        from_attributes = True


class AdminUserResponse(UserBase):
    """Response schema for admin users."""
    pass


class PlayerUserResponse(UserBase):
    """Response schema for player users."""
    group_id: Optional[UUID]
    payment_amount_ils: Optional[float]

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """Response after successful login."""
    user: UserBase
    access_token: str
    token_type: str = "bearer"


class UserListResponse(BaseModel):
    """Response for listing users."""
    users: list[UserBase]
    total: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str

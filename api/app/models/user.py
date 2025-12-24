# app/models/user.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base
from .enums import UserType


class User(Base):
    """Base user model with joined table inheritance"""
    
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    user_type = Column(Enum(UserType), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_on": user_type,
        "polymorphic_identity": None,
    }

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, type={self.user_type})>"


class AdminUser(User):
    """Admin user who creates and manages experiments"""
    
    __tablename__ = "admin_users"

    id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)

    # Relationships
    experiments = relationship("Experiment", back_populates="admin", cascade="all, delete-orphan")

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": UserType.ADMIN,
    }

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username={self.username})>"


class PlayerUser(User):
    """Player user who participates in experiments"""
    
    __tablename__ = "player_users"

    id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    group_id = Column(PG_UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True, index=True)
    payment_amount_ils = Column(Numeric(10, 2), nullable=True)

    # Relationships
    group = relationship("Group", back_populates="players")
    transactions = relationship("Transaction", back_populates="player", cascade="all, delete-orphan")
    currency_knowledge = relationship("PlayerCurrencyKnowledge", back_populates="player", cascade="all, delete-orphan")
    feedbacks = relationship("UserFeedback", back_populates="player", cascade="all, delete-orphan")
    balances = relationship("PlayerBalance", back_populates="player", cascade="all, delete-orphan")

    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": UserType.PLAYER,
    }

    def __repr__(self):
        return f"<PlayerUser(id={self.id}, username={self.username}, group_id={self.group_id})>"

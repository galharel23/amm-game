# app/models/round.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base


class Round(Base):
    """Logical round definition (applies to all groups)"""
    
    __tablename__ = "rounds"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(PG_UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False, index=True)
    round_number = Column(Integer, nullable=False)
    is_training_round = Column(Boolean, nullable=False, index=True)
    counts_for_payment = Column(Boolean, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    currency_x_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    currency_y_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    external_price_x = Column(Numeric(20, 8), nullable=False)
    external_price_y = Column(Numeric(20, 8), nullable=False)
    initial_reserve_x = Column(Numeric(20, 8), nullable=False)
    initial_reserve_y = Column(Numeric(20, 8), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    experiment = relationship("Experiment", back_populates="rounds")
    currency_x = relationship("Currency", foreign_keys=[currency_x_id])
    currency_y = relationship("Currency", foreign_keys=[currency_y_id])
    experiment_rounds = relationship("ExperimentRound", back_populates="round", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Round(id={self.id}, experiment_id={self.experiment_id}, number={self.round_number})>"


class ExperimentRound(Base):
    """Actual AMM pool instance for a specific group in a round"""
    
    __tablename__ = "experiment_rounds"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    round_id = Column(PG_UUID(as_uuid=True), ForeignKey("rounds.id"), nullable=False, index=True)
    group_id = Column(PG_UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False, index=True)
    reserve_x = Column(Numeric(20, 8), nullable=False)
    reserve_y = Column(Numeric(20, 8), nullable=False)
    k_constant = Column(Numeric(40, 16), nullable=False)
    transaction_fee_percent = Column(Numeric(5, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True, index=True)
    ended_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    round = relationship("Round", back_populates="experiment_rounds")
    group = relationship("Group", back_populates="experiment_rounds")
    transactions = relationship("Transaction", back_populates="experiment_round", cascade="all, delete-orphan")
    player_knowledge = relationship("PlayerCurrencyKnowledge", back_populates="experiment_round", cascade="all, delete-orphan")
    feedbacks = relationship("UserFeedback", back_populates="experiment_round", cascade="all, delete-orphan")
    player_balances = relationship("PlayerBalance", back_populates="experiment_round", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ExperimentRound(id={self.id}, round_id={self.round_id}, group_id={self.group_id})>"

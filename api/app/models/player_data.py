# app/models/player_data.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base


class PlayerCurrencyKnowledge(Base):
    """Tracks which currency price each player can see"""
    
    __tablename__ = "player_currency_knowledge"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("player_users.id"), nullable=False, index=True)
    experiment_round_id = Column(PG_UUID(as_uuid=True), ForeignKey("experiment_rounds.id"), nullable=False, index=True)
    revealed_currency_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    player = relationship("PlayerUser", back_populates="currency_knowledge")
    experiment_round = relationship("ExperimentRound", back_populates="player_knowledge")
    revealed_currency = relationship("Currency")

    def __repr__(self):
        return f"<PlayerCurrencyKnowledge(player_id={self.player_id}, round_id={self.experiment_round_id})>"


class PlayerBalance(Base):
    """Tracks currency holdings for each player in each experiment round"""
    
    __tablename__ = "player_balances"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("player_users.id"), nullable=False, index=True)
    experiment_round_id = Column(PG_UUID(as_uuid=True), ForeignKey("experiment_rounds.id"), nullable=False, index=True)
    currency_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    balance = Column(Numeric(20, 8), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    player = relationship("PlayerUser", back_populates="balances")
    experiment_round = relationship("ExperimentRound", back_populates="player_balances")
    currency = relationship("Currency")

    def __repr__(self):
        return f"<PlayerBalance(player_id={self.player_id}, currency_id={self.currency_id}, balance={self.balance})>"


class UserFeedback(Base):
    """Auto-generated feedback for players at end of each round"""
    
    __tablename__ = "user_feedbacks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("player_users.id"), nullable=False, index=True)
    experiment_round_id = Column(PG_UUID(as_uuid=True), ForeignKey("experiment_rounds.id"), nullable=False, index=True)
    feedback_items = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    player = relationship("PlayerUser", back_populates="feedbacks")
    experiment_round = relationship("ExperimentRound", back_populates="feedbacks")

    def __repr__(self):
        return f"<UserFeedback(player_id={self.player_id}, round_id={self.experiment_round_id})>"

# app/models/transaction.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base


class Transaction(Base):
    """Record of all swap transactions"""
    
    __tablename__ = "transactions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_round_id = Column(PG_UUID(as_uuid=True), ForeignKey("experiment_rounds.id"), nullable=False, index=True)
    player_id = Column(PG_UUID(as_uuid=True), ForeignKey("player_users.id"), nullable=False, index=True)
    currency_in_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    amount_in = Column(Numeric(20, 8), nullable=False)
    currency_out_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    amount_out = Column(Numeric(20, 8), nullable=False)
    price_ratio = Column(Numeric(20, 8), nullable=False)
    has_completed = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    experiment_round = relationship("ExperimentRound", back_populates="transactions")
    player = relationship("PlayerUser", back_populates="transactions")
    currency_in = relationship("Currency", foreign_keys=[currency_in_id])
    currency_out = relationship("Currency", foreign_keys=[currency_out_id])

    def __repr__(self):
        return f"<Transaction(id={self.id}, player_id={self.player_id}, amount_in={self.amount_in})>"

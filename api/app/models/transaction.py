# app/models/transaction.py

from datetime import datetime, timezone
from uuid import uuid4

# SQLAlchemy imports
from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base
from .enums import TransactionStatus, TransactionType


class Transaction(Base):
    """
    Represents a transaction (swap or liquidity management) in the system.
    """
    __tablename__ = "transactions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    pool_id = Column(PG_UUID(as_uuid=True), ForeignKey("pools.id"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    tx_type = Column(SQLEnum(TransactionType), nullable=False)
    amount_in = Column(Numeric(precision=30, scale=8), nullable=False)
    currency_in_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False)
    amount_out = Column(Numeric(precision=30, scale=8), nullable=False)
    currency_out_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False)
    price_execution = Column(Numeric(precision=30, scale=16), nullable=True)
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.EXECUTED)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    pool = relationship("Pool", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    currency_in = relationship("Currency", foreign_keys=[currency_in_id], back_populates="transactions_in")
    currency_out = relationship("Currency", foreign_keys=[currency_out_id], back_populates="transactions_out")

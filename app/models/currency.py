# app/models/currency.py

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base


class Currency(Base):
    """
    Represents a token/currency in the system.
    """
    __tablename__ = "currencies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    decimals = Column(Numeric(precision=3, scale=0), nullable=False, default=18)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    pools_as_x = relationship("Pool", foreign_keys="Pool.currency_x_id", back_populates="currency_x")
    pools_as_y = relationship("Pool", foreign_keys="Pool.currency_y_id", back_populates="currency_y")
    transactions_in = relationship("Transaction", foreign_keys="Transaction.currency_in_id", back_populates="currency_in")
    transactions_out = relationship("Transaction", foreign_keys="Transaction.currency_out_id", back_populates="currency_out")

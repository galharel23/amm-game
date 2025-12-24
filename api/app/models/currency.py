# app/models/currency.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .base import Base


class Currency(Base):
    """Trading currencies used in experiments"""
    
    __tablename__ = "currencies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name_en = Column(String(100), nullable=False)
    name_he = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Currency(id={self.id}, symbol={self.symbol})>"

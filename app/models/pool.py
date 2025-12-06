# app/models/pool.py

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base


class Pool(Base):
    """
    Represents a constant-product AMM pool with two assets X and Y.
    
    Invariant:
        x_reserve * y_reserve = K (constant)
    """
    __tablename__ = "pools"
    __table_args__ = (
        UniqueConstraint("currency_x_id", "currency_y_id", name="uq_pool_currencies"),
    )

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    currency_x_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    currency_y_id = Column(PG_UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False, index=True)
    x_reserve = Column(Numeric(precision=30, scale=8), nullable=False, default=0)
    y_reserve = Column(Numeric(precision=30, scale=8), nullable=False, default=0)
    K = Column(Numeric(precision=60, scale=16), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    currency_x = relationship("Currency", foreign_keys=[currency_x_id], back_populates="pools_as_x")
    currency_y = relationship("Currency", foreign_keys=[currency_y_id], back_populates="pools_as_y")
    transactions = relationship("Transaction", back_populates="pool")

    def price_x_in_y(self) -> Decimal:
        """Returns the instantaneous price of 1 unit of X in terms of Y (y/x)."""
        if self.x_reserve == 0:
            return Decimal(0)
        return self.y_reserve / self.x_reserve

    def price_y_in_x(self) -> Decimal:
        """Returns the instantaneous price of 1 unit of Y in terms of X (x/y)."""
        if self.y_reserve == 0:
            return Decimal(0)
        return self.x_reserve / self.y_reserve

    def swap_x_for_y(self, dx: Decimal) -> Decimal:
        """
        User sends dx units of X into the pool and receives Δy units of Y.
        
        :param dx: Amount of X sent to the pool (must be > 0).
        :return: Amount of Y the user receives.
        """
        if dx <= 0:
            raise ValueError("dx must be positive.")

        x_new = self.x_reserve + dx
        y_new = self.K / x_new
        dy = self.y_reserve - y_new

        # Update reserves
        self.x_reserve = x_new
        self.y_reserve = y_new

        return dy

    def swap_y_for_x(self, dy: Decimal) -> Decimal:
        """
        User sends dy units of Y into the pool and receives Δx units of X.
        
        :param dy: Amount of Y sent to the pool (must be > 0).
        :return: Amount of X the user receives.
        """
        if dy <= 0:
            raise ValueError("dy must be positive.")

        y_new = self.y_reserve + dy
        x_new = self.K / y_new
        dx = self.x_reserve - x_new

        # Update reserves
        self.y_reserve = y_new
        self.x_reserve = x_new

        return dx

    def add_liquidity(self, dx: Decimal, dy: Decimal) -> None:
        """Add liquidity to the pool (management function)."""
        if dx < 0 or dy < 0:
            raise ValueError("Amounts must be non-negative.")
        
        self.x_reserve += dx
        self.y_reserve += dy
        self.K = self.x_reserve * self.y_reserve
        self.updated_at = datetime.now(timezone.utc)

    def remove_liquidity(self, dx: Decimal, dy: Decimal) -> None:
        """Remove liquidity from the pool (management function)."""
        if dx < 0 or dy < 0:
            raise ValueError("Amounts must be non-negative.")
        if self.x_reserve < dx or self.y_reserve < dy:
            raise ValueError("Insufficient reserves to remove.")
        
        self.x_reserve -= dx
        self.y_reserve -= dy
        self.K = self.x_reserve * self.y_reserve
        self.updated_at = datetime.now(timezone.utc)

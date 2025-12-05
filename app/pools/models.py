# app/pools/models.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class LiquidityPool:
    """
    Domain model representing a constant-product AMM pool with two assets X and Y.

    Invariant:
        x_reserve * y_reserve = K (constant)

    No trading fees are applied in this version.
    """
    id: UUID = field(default_factory=uuid4)
    x_reserve: float = field(default=0.0)
    y_reserve: float = field(default=0.0)
    K: float = field(init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.x_reserve <= 0 or self.y_reserve <= 0:
            raise ValueError("Initial reserves must be positive.")
        self.x_reserve = float(self.x_reserve)
        self.y_reserve = float(self.y_reserve)
        self.K = self.x_reserve * self.y_reserve

    # --------- Pricing helpers --------- #

    def price_x_in_y(self) -> float:
        """
        Returns the instantaneous price of 1 unit of X in terms of Y (y/x).
        """
        return self.y_reserve / self.x_reserve

    def price_y_in_x(self) -> float:
        """
        Returns the instantaneous price of 1 unit of Y in terms of X (x/y).
        """
        return self.x_reserve / self.y_reserve

    # --------- Swaps --------- #

    def swap_x_for_y(self, dx: float) -> float:
        """
        User sends dx units of X into the pool and receives Δy units of Y.

        Enforces:
            (x_reserve + dx) * y_new = K
            y_new = K / (x_reserve + dx)
            Δy = y_reserve - y_new

        :param dx: Amount of X sent to the pool (must be > 0).
        :return: Amount of Y the user receives.
        """
        if dx <= 0:
            raise ValueError("dx must be positive.")

        x_new = self.x_reserve + dx
        y_new = self.K / x_new
        dy = self.y_reserve - y_new  # amount of Y the user receives

        # Update reserves
        self.x_reserve = x_new
        self.y_reserve = y_new

        return dy

    def swap_y_for_x(self, dy: float) -> float:
        """
        User sends dy units of Y into the pool and receives Δx units of X.

        Enforces:
            (y_reserve + dy) * x_new = K
            x_new = K / (y_reserve + dy)
            Δx = x_reserve - x_new

        :param dy: Amount of Y sent to the pool (must be > 0).
        :return: Amount of X the user receives.
        """
        if dy <= 0:
            raise ValueError("dy must be positive.")

        y_new = self.y_reserve + dy
        x_new = self.K / y_new
        dx = self.x_reserve - x_new  # amount of X the user receives

        # Update reserves
        self.y_reserve = y_new
        self.x_reserve = x_new

        return dx

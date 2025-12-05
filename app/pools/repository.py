# app/pools/repository.py

from __future__ import annotations

from typing import Dict
from uuid import UUID

from .models import LiquidityPool


class PoolNotFoundError(Exception):
    """Raised when a pool with the given id does not exist."""
    pass


class PoolRepository:
    """
    Simple in-memory repository for LiquidityPool objects.

    This is the place you would later swap out for a real database
    (e.g., SQLAlchemy, Prisma, etc.).
    """

    def __init__(self) -> None:
        self._pools: Dict[UUID, LiquidityPool] = {}

    # ---- CRUD-like operations ---- #

    def create_pool(self, x_init: float, y_init: float) -> LiquidityPool:
        pool = LiquidityPool(x_reserve=x_init, y_reserve=y_init)
        self._pools[pool.id] = pool
        return pool

    def get_pool(self, pool_id: UUID) -> LiquidityPool:
        try:
            return self._pools[pool_id]
        except KeyError:
            raise PoolNotFoundError(f"Pool with id {pool_id} not found.")


# Global repository instance (for this small project)
pool_repository = PoolRepository()

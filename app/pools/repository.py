# app/pools/repository.py

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models import Currency, Pool


class PoolNotFoundError(Exception):
    """Raised when a pool with the given id does not exist."""
    pass


def get_or_create_currency(db: Session, symbol: str, name: Optional[str] = None) -> Currency:
    symbol = symbol.upper()
    cur = db.query(Currency).filter(Currency.symbol == symbol).one_or_none()
    if cur:
        return cur

    cur = Currency(symbol=symbol, name=(name or symbol), decimals=18)
    db.add(cur)
    db.flush()
    return cur


def create_pool(db: Session, x_init: float, y_init: float, currency_x: str = "XTK", currency_y: str = "YTK") -> Pool:
    """Create a Pool in the database. Ensures currencies exist."""
    # ensure currencies exist
    cx = get_or_create_currency(db, currency_x)
    cy = get_or_create_currency(db, currency_y)

    pool = Pool(
        id=uuid4(),
        currency_x_id=cx.id,
        currency_y_id=cy.id,
        x_reserve=x_init,
        y_reserve=y_init,
        K=x_init * y_init,
        is_active=True,
    )
    db.add(pool)
    db.commit()
    db.refresh(pool)
    return pool


def get_pool(db: Session, pool_id: UUID) -> Pool:
    pool = db.query(Pool).filter(Pool.id == pool_id).one_or_none()
    if pool is None:
        raise PoolNotFoundError(f"Pool with id {pool_id} not found.")
    return pool

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


def create_currency(db: Session, symbol: str, name: str, image_url: str | None = None) -> Currency:
    """
    Create a new currency in the database.
    
    :param db: Database session
    :param symbol: Currency symbol (must be unique)
    :param name: Currency name (must be unique)
    :param image_url: Optional URL to currency image
    :return: Created Currency object
    :raises ValueError: If symbol or name already exists
    """
    symbol = symbol.upper().strip()
    name = name.strip()
    
    # Validate symbol uniqueness
    existing_symbol = db.query(Currency).filter(Currency.symbol == symbol).one_or_none()
    if existing_symbol:
        raise ValueError(f"Currency with symbol '{symbol}' already exists.")
    
    # Validate name uniqueness
    existing_name = db.query(Currency).filter(Currency.name == name).one_or_none()
    if existing_name:
        raise ValueError(f"Currency with name '{name}' already exists.")
    
    currency = Currency(
        symbol=symbol,
        name=name,
        image_url=image_url,
    )
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


def create_pool(db: Session, currency_x_id: UUID, currency_y_id: UUID, x_init: float, y_init: float) -> Pool:
    """Create a Pool in the database using existing currency IDs."""
    # Validate currencies are different
    if currency_x_id == currency_y_id:
        raise ValueError("Currency X and Currency Y must be different.")
    
    # Validate currencies exist
    cx = db.query(Currency).filter(Currency.id == currency_x_id).one_or_none()
    if cx is None:
        raise ValueError(f"Currency X with id {currency_x_id} not found.")
    
    cy = db.query(Currency).filter(Currency.id == currency_y_id).one_or_none()
    if cy is None:
        raise ValueError(f"Currency Y with id {currency_y_id} not found.")

    # Check if pool already exists for this currency pair
    existing_pool = db.query(Pool).filter(
        Pool.currency_x_id == currency_x_id,
        Pool.currency_y_id == currency_y_id,
    ).one_or_none()
    
    if existing_pool:
        raise ValueError(f"Pool for {cx.symbol}/{cy.symbol} already exists.")

    pool = Pool(
        id=uuid4(),
        currency_x_id=currency_x_id,
        currency_y_id=currency_y_id,
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
    """Retrieve a single pool by id."""
    pool = db.query(Pool).filter(Pool.id == pool_id).one_or_none()
    if pool is None:
        raise PoolNotFoundError(f"Pool with id {pool_id} not found.")
    return pool


def get_all_pools(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Pool], int]:
    """Retrieve all pools with pagination. Returns (pools, total_count)."""
    query = db.query(Pool)
    total = query.count()
    pools = query.offset(skip).limit(limit).all()
    return pools, total


def get_all_currencies(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Currency], int]:
    """Retrieve all currencies with pagination. Returns (currencies, total_count)."""
    query = db.query(Currency)
    total = query.count()
    currencies = query.offset(skip).limit(limit).all()
    return currencies, total


def get_available_currencies(db: Session, skip: int = 0, limit: int = 100) -> tuple[list[Currency], int]:
    """
    Retrieve currencies not attached to any pool (available for new pools).
    Returns (currencies, total_count).
    """
    # Get all currency IDs used in pools
    used_currency_ids = db.query(Pool.currency_x_id).union(
        db.query(Pool.currency_y_id)
    ).all()
    used_ids = [row[0] for row in used_currency_ids]
    
    # Query currencies not in used_ids
    query = db.query(Currency)
    if used_ids:
        query = query.filter(Currency.id.notin_(used_ids))
    
    total = query.count()
    currencies = query.offset(skip).limit(limit).all()
    return currencies, total

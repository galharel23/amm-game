# app/pools/routes.py

from __future__ import annotations

from uuid import UUID

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from .schemas import (
    PoolCreate,
    PoolState,
    SwapXForYRequest,
    SwapYForXRequest,
    SwapXForYResponse,
    SwapYForXResponse,
)
from .repository import create_pool as repo_create_pool, get_pool as repo_get_pool, PoolNotFoundError
from app.database import get_db

router = APIRouter()


# --------- Helper: domain -> API schema --------- #

def pool_to_state(pool) -> PoolState:
    """
    Convert a SQLAlchemy `Pool` object to a `PoolState` schema.
    """
    # convert numerics/decimals to float for API readability
    def to_float(v):
        if v is None:
            return 0.0
        if isinstance(v, Decimal):
            return float(v)
        try:
            return float(v)
        except Exception:
            return v

    return PoolState(
        id=pool.id,
        x_reserve=to_float(pool.x_reserve),
        y_reserve=to_float(pool.y_reserve),
        K=to_float(pool.K),
        price_x_in_y=to_float(pool.price_x_in_y()),
        price_y_in_x=to_float(pool.price_y_in_x()),
        created_at=pool.created_at,
    )


# --------- Routes --------- #

@router.post("/", response_model=PoolState)
def create_pool(req: PoolCreate, db: Session = Depends(get_db)) -> PoolState:
    """
    Create a new liquidity pool with initial X and Y reserves.

    - Enforces that reserves are > 0 (via validation).
    - Returns the full pool state, including its generated id.
    """
    try:
        pool = repo_create_pool(db, req.x_init, req.y_init)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return pool_to_state(pool)


@router.get("/{pool_id}", response_model=PoolState)
def get_pool_state(pool_id: UUID, db: Session = Depends(get_db)) -> PoolState:
    """
    Get the current state of a specific pool by its id.
    """
    try:
        pool = repo_get_pool(db, pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return pool_to_state(pool)


@router.post("/{pool_id}/swap/x-for-y", response_model=SwapXForYResponse)
def swap_x_for_y(pool_id: UUID, req: SwapXForYRequest, db: Session = Depends(get_db)) -> SwapXForYResponse:
    """
    Swap token X for token Y in the given pool.

    The user sends `amount_in` units of X and receives `amount_out` units of Y,
    according to the constant-product rule x * y = K.
    """
    try:
        pool = repo_get_pool(db, pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        amount_out = pool.swap_x_for_y(req.amount_in)
    except ValueError as e:
        # e.g., amount_in <= 0
        raise HTTPException(status_code=400, detail=str(e))

    # persist updated reserves
    db.add(pool)
    db.commit()
    db.refresh(pool)

    return SwapXForYResponse(
        pool=pool_to_state(pool),
        amount_in=req.amount_in,
        amount_out=float(amount_out),
    )


@router.post("/{pool_id}/swap/y-for-x", response_model=SwapYForXResponse)
def swap_y_for_x(pool_id: UUID, req: SwapYForXRequest, db: Session = Depends(get_db)) -> SwapYForXResponse:
    """
    Swap token Y for token X in the given pool.

    The user sends `amount_in` units of Y and receives `amount_out` units of X,
    according to the constant-product rule x * y = K.
    """
    try:
        pool = repo_get_pool(db, pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        amount_out = pool.swap_y_for_x(req.amount_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # persist updated reserves
    db.add(pool)
    db.commit()
    db.refresh(pool)

    return SwapYForXResponse(
        pool=pool_to_state(pool),
        amount_in=req.amount_in,
        amount_out=float(amount_out),
    )

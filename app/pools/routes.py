# app/pools/routes.py

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from .models import LiquidityPool
from .schemas import (
    PoolCreate,
    PoolState,
    SwapXForYRequest,
    SwapYForXRequest,
    SwapXForYResponse,
    SwapYForXResponse,
)
from .repository import pool_repository, PoolNotFoundError

router = APIRouter()


# --------- Helper: domain -> API schema --------- #

def pool_to_state(pool: LiquidityPool) -> PoolState:
    """
    Convert a domain LiquidityPool object to a PoolState schema.
    """
    return PoolState(
        id=pool.id,
        x_reserve=pool.x_reserve,
        y_reserve=pool.y_reserve,
        K=pool.K,
        price_x_in_y=pool.price_x_in_y(),
        price_y_in_x=pool.price_y_in_x(),
        created_at=pool.created_at,
    )


# --------- Routes --------- #

@router.post("/", response_model=PoolState)
def create_pool(req: PoolCreate) -> PoolState:
    """
    Create a new liquidity pool with initial X and Y reserves.

    - Enforces that reserves are > 0 (via validation).
    - Returns the full pool state, including its generated id.
    """
    try:
        pool = pool_repository.create_pool(req.x_init, req.y_init)
    except ValueError as e:
        # This comes from the domain layer (__post_init__) if something is invalid.
        raise HTTPException(status_code=400, detail=str(e))

    return pool_to_state(pool)


@router.get("/{pool_id}", response_model=PoolState)
def get_pool_state(pool_id: UUID) -> PoolState:
    """
    Get the current state of a specific pool by its id.
    """
    try:
        pool = pool_repository.get_pool(pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return pool_to_state(pool)


@router.post("/{pool_id}/swap/x-for-y", response_model=SwapXForYResponse)
def swap_x_for_y(pool_id: UUID, req: SwapXForYRequest) -> SwapXForYResponse:
    """
    Swap token X for token Y in the given pool.

    The user sends `amount_in` units of X and receives `amount_out` units of Y,
    according to the constant-product rule x * y = K.
    """
    try:
        pool = pool_repository.get_pool(pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        amount_out = pool.swap_x_for_y(req.amount_in)
    except ValueError as e:
        # e.g., amount_in <= 0
        raise HTTPException(status_code=400, detail=str(e))

    return SwapXForYResponse(
        pool=pool_to_state(pool),
        amount_in=req.amount_in,
        amount_out=amount_out,
    )


@router.post("/{pool_id}/swap/y-for-x", response_model=SwapYForXResponse)
def swap_y_for_x(pool_id: UUID, req: SwapYForXRequest) -> SwapYForXResponse:
    """
    Swap token Y for token X in the given pool.

    The user sends `amount_in` units of Y and receives `amount_out` units of X,
    according to the constant-product rule x * y = K.
    """
    try:
        pool = pool_repository.get_pool(pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        amount_out = pool.swap_y_for_x(req.amount_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return SwapYForXResponse(
        pool=pool_to_state(pool),
        amount_in=req.amount_in,
        amount_out=amount_out,
    )

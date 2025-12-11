# app/pools/routes.py

from __future__ import annotations

from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from .schemas import (
    PoolCreate,
    PoolState,
    PoolListResponse,
    ErrorResponse,
    SwapXForYRequest,
    SwapYForXRequest,
    SwapXForYResponse,
    SwapYForXResponse,
    CurrencyState,
    CurrencyListResponse,
    CurrencyCreate,
)
from .repository import (
    create_pool as repo_create_pool,
    get_pool as repo_get_pool,
    get_all_pools as repo_get_all_pools,
    get_all_currencies,
    get_available_currencies,
    create_currency as repo_create_currency,
    PoolNotFoundError,
)
from app.database import get_db
from app.models import Transaction, TransactionType, TransactionStatus, Currency

router = APIRouter()


# --------- Helper: domain -> API schema --------- #

def pool_to_state(pool) -> PoolState:
    """Convert a SQLAlchemy Pool object to a PoolState schema."""
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
        # NEW: currency metadata from relationships
        currency_x_id=pool.currency_x_id,
        currency_y_id=pool.currency_y_id,
        currency_x_symbol=pool.currency_x.symbol,
        currency_y_symbol=pool.currency_y.symbol,
        currency_x_name=pool.currency_x.name,
        currency_y_name=pool.currency_y.name,

        x_reserve=to_float(pool.x_reserve),
        y_reserve=to_float(pool.y_reserve),
        K=to_float(pool.K),
        price_x_in_y=to_float(pool.price_x_in_y()),
        price_y_in_x=to_float(pool.price_y_in_x()),
        is_active=pool.is_active,
        created_at=pool.created_at,
    )


def create_transaction_record(
    db: Session,
    pool_id: UUID,
    tx_type: TransactionType,
    currency_in_id: UUID,
    currency_out_id: UUID,
    amount_in: Decimal,
    amount_out: Decimal,
) -> Transaction:
    """Create and persist a transaction record."""
    price_execution = amount_out / amount_in if amount_in > 0 else Decimal(0)

    transaction = Transaction(
        pool_id=pool_id,
        user_id=None,  # No user context for now
        tx_type=tx_type,
        amount_in=amount_in,
        currency_in_id=currency_in_id,
        amount_out=amount_out,
        currency_out_id=currency_out_id,
        price_execution=price_execution,
        status=TransactionStatus.EXECUTED,
        executed_at=datetime.now(timezone.utc),
    )
    db.add(transaction)
    return transaction


# --------- Routes --------- #

@router.post("/", response_model=PoolState, responses={400: {"model": ErrorResponse}})
def create_pool(req: PoolCreate, db: Session = Depends(get_db)) -> PoolState:
    """
    Create a new liquidity pool with initial X and Y reserves.

    - Requires valid currency IDs for both X and Y.
    - Enforces that reserves are > 0 (via validation).
    - Returns the full pool state, including its generated id.
    """
    try:
        pool = repo_create_pool(db, req.currency_x_id, req.currency_y_id, req.x_init, req.y_init)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid pool creation", "detail": str(e), "status_code": 400}
        )

    return pool_to_state(pool)


@router.get("/", response_model=PoolListResponse)
def list_pools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> PoolListResponse:
    """
    List all pools with pagination.

    - `skip`: Number of pools to skip (default: 0)
    - `limit`: Maximum number of pools to return (default: 100, max: 1000)
    """
    if limit > 1000:
        limit = 1000
    if skip < 0:
        skip = 0

    pools, total = repo_get_all_pools(db, skip=skip, limit=limit)
    return PoolListResponse(
        pools=[pool_to_state(pool) for pool in pools],
        total=total,
    )


@router.get("/{pool_id}", response_model=PoolState, responses={404: {"model": ErrorResponse}})
def get_pool_state(pool_id: UUID, db: Session = Depends(get_db)) -> PoolState:
    """
    Get the current state of a specific pool by its id.
    """
    try:
        pool = repo_get_pool(db, pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": "Pool not found", "detail": str(e), "status_code": 404}
        )

    return pool_to_state(pool)


@router.post("/{pool_id}/swap/x-for-y", response_model=SwapXForYResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
def swap_x_for_y(pool_id: UUID, req: SwapXForYRequest, db: Session = Depends(get_db)) -> SwapXForYResponse:
    """
    Swap token X for token Y in the given pool.

    The user sends `amount_in` units of X and receives `amount_out` units of Y,
    according to the constant-product rule x * y = K.

    - `min_amount_out`: Minimum acceptable output (slippage protection).
      If actual output < min_amount_out, the swap fails.
    """
    try:
        pool = repo_get_pool(db, pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": "Pool not found", "detail": str(e), "status_code": 404}
        )

    try:
        amount_in_decimal = Decimal(str(req.amount_in))
        amount_out = pool.swap_x_for_y(amount_in_decimal)

        # Validate slippage tolerance
        if amount_out < Decimal(str(req.min_amount_out)):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Slippage exceeded",
                    "detail": f"Expected minimum {req.min_amount_out}, but got {float(amount_out)}",
                    "status_code": 400,
                }
            )

        # Persist updated reserves
        db.add(pool)

        # Create transaction record
        create_transaction_record(
            db,
            pool_id=pool.id,
            tx_type=TransactionType.SWAP,
            currency_in_id=pool.currency_x_id,
            currency_out_id=pool.currency_y_id,
            amount_in=amount_in_decimal,
            amount_out=amount_out,
        )

        db.commit()
        db.refresh(pool)

        price_execution = float(amount_out) / req.amount_in if req.amount_in > 0 else 0.0

        return SwapXForYResponse(
            pool=pool_to_state(pool),
            amount_in=req.amount_in,
            amount_out=float(amount_out),
            price_execution=price_execution,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid swap parameters", "detail": str(e), "status_code": 400}
        )


@router.post("/{pool_id}/swap/y-for-x", response_model=SwapYForXResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
def swap_y_for_x(pool_id: UUID, req: SwapYForXRequest, db: Session = Depends(get_db)) -> SwapYForXResponse:
    """
    Swap token Y for token X in the given pool.

    The user sends `amount_in` units of Y and receives `amount_out` units of X,
    according to the constant-product rule x * y = K.

    - `min_amount_out`: Minimum acceptable output (slippage protection).
      If actual output < min_amount_out, the swap fails.
    """
    try:
        pool = repo_get_pool(db, pool_id)
    except PoolNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={"error": "Pool not found", "detail": str(e), "status_code": 404}
        )

    try:
        amount_in_decimal = Decimal(str(req.amount_in))
        amount_out = pool.swap_y_for_x(amount_in_decimal)

        # Validate slippage tolerance
        if amount_out < Decimal(str(req.min_amount_out)):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Slippage exceeded",
                    "detail": f"Expected minimum {req.min_amount_out}, but got {float(amount_out)}",
                    "status_code": 400,
                }
            )

        # Persist updated reserves
        db.add(pool)

        # Create transaction record
        create_transaction_record(
            db,
            pool_id=pool.id,
            tx_type=TransactionType.SWAP,
            currency_in_id=pool.currency_y_id,
            currency_out_id=pool.currency_x_id,
            amount_in=amount_in_decimal,
            amount_out=amount_out,
        )

        db.commit()
        db.refresh(pool)

        price_execution = float(amount_out) / req.amount_in if req.amount_in > 0 else 0.0

        return SwapYForXResponse(
            pool=pool_to_state(pool),
            amount_in=req.amount_in,
            amount_out=float(amount_out),
            price_execution=price_execution,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid swap parameters", "detail": str(e), "status_code": 400}
        )


# --------- Currency endpoints --------- #

@router.post("/currencies/", response_model=CurrencyState, responses={400: {"model": ErrorResponse}})
def create_currency(req: CurrencyCreate, db: Session = Depends(get_db)) -> CurrencyState:
    """
    Create a new currency in the system.

    - `symbol`: Unique currency symbol (e.g., 'BTC', 'ETH'). Will be converted to uppercase.
    - `name`: Unique currency full name (e.g., 'Bitcoin').
    - `image_url`: Optional URL to currency logo/image.

    Returns the created currency with its id.
    """
    try:
        currency = repo_create_currency(db, req.symbol, req.name, req.image_url)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid currency creation", "detail": str(e), "status_code": 400}
        )

    pools_count = len(currency.pools_as_x) + len(currency.pools_as_y)
    
    return CurrencyState(
        id=currency.id,
        symbol=currency.symbol,
        name=currency.name,
        decimals=float(currency.decimals),
        image_url=currency.image_url,
        pools_count=pools_count,
        created_at=currency.created_at,
    )


@router.get("/currencies/", response_model=CurrencyListResponse)
def list_currencies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> CurrencyListResponse:
    """
    List all available currencies with pagination.

    - `skip`: Number of currencies to skip (default: 0)
    - `limit`: Maximum number of currencies to return (default: 100, max: 1000)
    """
    if limit > 1000:
        limit = 1000
    if skip < 0:
        skip = 0

    currencies, total = get_all_currencies(db, skip=skip, limit=limit)
    return CurrencyListResponse(
        currencies=[
            CurrencyState(
                id=c.id,
                symbol=c.symbol,
                name=c.name,
                decimals=float(c.decimals),
                image_url=c.image_url,
                pools_count=len(c.pools_as_x) + len(c.pools_as_y),
                created_at=c.created_at,
            )
            for c in currencies
        ],
        total=total,
    )


@router.get("/currencies/available", response_model=CurrencyListResponse)
def list_available_currencies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> CurrencyListResponse:
    """
    List all currencies NOT yet attached to any pool (available for creating new pools).

    - `skip`: Number of currencies to skip (default: 0)
    - `limit`: Maximum number of currencies to return (default: 100, max: 1000)
    """
    if limit > 1000:
        limit = 1000
    if skip < 0:
        skip = 0

    currencies, total = get_available_currencies(db, skip=skip, limit=limit)
    return CurrencyListResponse(
        currencies=[
            CurrencyState(
                id=c.id,
                symbol=c.symbol,
                name=c.name,
                decimals=float(c.decimals),
                image_url=c.image_url,
                pools_count=0,  # By definition, available currencies have 0 pools
                created_at=c.created_at,
            )
            for c in currencies
        ],
        total=total,
    )

# app/models/enums.py

from enum import Enum


class TransactionType(str, Enum):
    """Types of transactions in the pool."""
    SWAP = "SWAP"
    ADD_LIQUIDITY = "ADD_LIQUIDITY"
    REMOVE_LIQUIDITY = "REMOVE_LIQUIDITY"


class TransactionStatus(str, Enum):
    """Status of a transaction."""
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"

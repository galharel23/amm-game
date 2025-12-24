# AMM Game - Copilot Instructions

## Project Overview

This is a blockchain financial experiment platform with an Automated Market Maker (AMM) simulation. The system enables researchers to run controlled experiments where participants interact with AMM pools in real-time.

### Core Concepts
- **Experiment Environment**: Controlled blockchain/DeFi simulation
- **Two User Types**: Experiment Managers (admins) and Participants (users)
- **Real-time Interaction**: Live updates and synchronized state
- **AMM Mechanics**: Constant-product market maker (x * y = k)

## Architecture

### Project Structure
```
amm-game/
├── api/                          # Backend (FastAPI + PostgreSQL)
│   ├── app/
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py         # User, AdminUser, PlayerUser
│   │   │   ├── currency.py     # Currency
│   │   │   ├── experiment.py   # Experiment, Group
│   │   │   ├── round.py        # Round, ExperimentRound
│   │   │   ├── transaction.py  # Transaction
│   │   │   ├── player_data.py  # PlayerBalance, PlayerCurrencyKnowledge, UserFeedback
│   │   │   └── enums.py        # UserType, TransactionType, TransactionStatus
│   │   ├── pools/               # (Legacy) Pool-related endpoints
│   │   ├── admin/               # (Future) Admin endpoints
│   │   ├── participants/        # (Future) Participant endpoints
│   │   └── websocket/           # (Future) Real-time updates
│   ├── migrations/              # Alembic migrations
│   ├── venv/                    # Python virtual environment
│   └── DATABASE_SCHEMA.md       # Complete database documentation
│
├── manager-ui/                   # (Future) Admin dashboard
├── participant-ui/               # (Future) amm-game-frontend renamed
└── copilot-instructions.md      # This file
```

### Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL (via Docker)
- SQLAlchemy ORM
- Alembic migrations
- WebSockets (future)

**Frontend:**
- React + TypeScript
- Vite
- Axios for API calls
- React Router

**Infrastructure:**
- Docker + Docker Compose
- pgAdmin for DB management

## Coding Standards

### Python (Backend)

**Naming Conventions:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**Type Hints:**
- Always use type hints for function parameters and returns
- Use `from __future__ import annotations` for forward references

**Comments:**
- Add docstrings for all classes and functions
- Explain "why" not "what" in inline comments
- Document complex business logic

**Example:**
```python
from __future__ import annotations
from typing import Optional

def calculate_swap_output(
    input_amount: float,
    input_reserve: float,
    output_reserve: float,
    fee_percent: float = 0.3
) -> float:
    """
    Calculate output amount for constant-product AMM swap.
    
    Uses the formula: dy = (y * dx * (1 - fee)) / (x + dx * (1 - fee))
    where x, y are reserves and dx is input amount.
    
    Args:
        input_amount: Amount of input token
        input_reserve: Reserve of input token in pool
        output_reserve: Reserve of output token in pool
        fee_percent: Trading fee percentage (default 0.3%)
        
    Returns:
        Amount of output token to receive
    """
    # Apply fee to input
    input_with_fee = input_amount * (1 - fee_percent / 100)
    
    # Constant product formula
    output = (output_reserve * input_with_fee) / (input_reserve + input_with_fee)
    
    return output
```

### TypeScript/React (Frontend)

**Naming Conventions:**
- Files: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Types/Interfaces: `PascalCase`

**Comments:**
- JSDoc for complex functions
- Explain state management logic
- Document API integration patterns

**Example:**
```typescript
interface SwapFormProps {
  poolId: string;
  onSuccess: () => void;
}

/**
 * Swap form component for executing token swaps in AMM pool.
 * Validates input amounts and displays price impact.
 */
export function SwapForm({ poolId, onSuccess }: SwapFormProps) {
  // Component logic
}
```

## Database Patterns

### Models
- One model per file in `api/app/models/`
- Use UUIDs for primary keys
- Add `created_at` and `updated_at` timestamps
- Use enums for status fields
- Add indexes for foreign keys and frequently queried fields

### Relationships
- Use SQLAlchemy relationships with `back_populates`
- Lazy load by default, eager load when needed
- Add cascade rules explicitly

### Migrations
- Always review auto-generated migrations
- Test migrations on dev database first
- Add data migrations when needed (not just schema)
- Never edit applied migrations - create new ones

**Workflow:**
```bash
# 1. Modify model in api/app/models/
# 2. Generate migration
python -m alembic revision --autogenerate -m "description"

# 3. Review generated file in api/migrations/versions/
# 4. Apply migration
python -m alembic upgrade head
```

## API Design

### REST Endpoints

**Structure:**
```
/pools/                    # Pool operations
/admin/                    # Admin-only endpoints (future)
/participants/             # Participant endpoints (future)
/experiments/              # Experiment management (future)
```

**Patterns:**
- Use FastAPI routers in separate files
- Group by resource/domain
- Use Pydantic schemas for validation
- Return consistent response formats
- Handle errors with HTTPException

**Example:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pools", tags=["pools"])

@router.get("/{pool_id}")
async def get_pool(
    pool_id: str,
    db: Session = Depends(get_db)
) -> PoolResponse:
    """
    Get pool details by ID.
    Returns current reserves, total liquidity, and recent transactions.
    """
    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=404, detail="Pool not found")
    
    return PoolResponse.from_orm(pool)
```

### Real-Time Updates (Future)

**WebSocket Strategy:**
- Use FastAPI WebSocket support
- Implement connection manager for room-based broadcasting
- Send updates on: swaps, liquidity changes, experiment state
- Handle reconnection gracefully

**Topics:**
- `pool:{pool_id}` - Pool-specific updates
- `experiment:{exp_id}` - Experiment-wide updates
- `admin` - Admin dashboard updates

## Security & Concurrency

### Transaction Locking
- Use database transactions for concurrent operations
- Lock pool records during swaps: `SELECT ... FOR UPDATE`
- Validate reserves haven't changed before committing
- Return clear errors on conflict

**Example:**
```python
from sqlalchemy.orm import Session

def execute_swap(pool_id: str, amount: float, db: Session):
    """Execute swap with optimistic locking."""
    # Lock the pool row
    pool = db.query(Pool).filter(Pool.id == pool_id).with_for_update().first()
    
    if not pool:
        raise ValueError("Pool not found")
    
    # Validate and execute swap
    if pool.reserve_x < amount:
        raise ValueError("Insufficient liquidity")
    
    # Update reserves
    pool.reserve_x += amount
    pool.reserve_y -= calculate_output(amount, pool)
    
    # Commit transaction
    db.commit()
```

### Authentication (Future)
- JWT tokens for API authentication
- Role-based access: `admin`, `participant`
- Separate endpoints by role
- Validate permissions on every request

## Two-UI Strategy

### Manager UI (Future: `manager-ui/`)
**Purpose:** Experiment configuration and monitoring

**Features:**
- Create/configure experiments
- Assign participants
- Monitor real-time activity
- View analytics and results
- Control experiment state (start/pause/end)

### Participant UI (Current: `amm-game-frontend/`)
**Purpose:** User interaction with experiments

**Features:**
- View available pools
- Execute swaps
- Add/remove liquidity
- View transaction history
- Real-time price updates

### Shared Patterns
- Same API client configuration
- Shared types/interfaces (consider npm workspace)
- Consistent styling/component library
- Both connect to same backend

## Development Workflow

### When Adding Features

1. **Backend:**
   - Update/create models
   - Generate migration
   - Add routes with validation
   - Test with `/docs` endpoint
   
2. **Frontend:**
   - Add types matching backend schemas
   - Create UI components
   - Integrate with API client
   - Test user flow

3. **Real-time:**
   - Add WebSocket event types
   - Implement server-side broadcast
   - Add client-side listeners

### Testing Strategy
- Test database constraints
- Test concurrent operations
- Validate AMM math formulas
- Test user permissions
- Test WebSocket reconnection

## Domain Knowledge

### AMM Mechanics
- Constant product: `x * y = k`
- Price: `price = y / x`
- Slippage increases with trade size
- Liquidity providers earn fees
- Impermanent loss for LPs

### Experiment Context
- Multiple experiments can run simultaneously
- Each experiment has isolated state
- Participants can only see their assigned experiments
- Managers see aggregated data across participants
- All data stored in single database with proper relationships

## Common Tasks

### Add New Model
1. Create file in `api/app/models/`
2. Import in `api/app/models/__init__.py`
3. Generate migration: `python -m alembic revision --autogenerate -m "add model"`
4. Review and apply: `python -m alembic upgrade head`

### Add New Endpoint
1. Create router in appropriate module
2. Add Pydantic schemas
3. Implement business logic
4. Register router in `main.py`
5. Test at `/docs`

### Add New Frontend Page
1. Create component in `src/pages/`
2. Add route in routing configuration
3. Create API client methods
4. Integrate data fetching
5. Add navigation link

## Questions to Ask

When implementing features, consider:
- **Concurrency:** Can multiple users do this simultaneously?
- **Real-time:** Should others see this update immediately?
- **Permissions:** Who can access this?
- **Validation:** What constraints should be enforced?
- **Rollback:** How do we undo this if needed?

## DO's and DON'Ts

### DO
✅ Use type hints everywhere
✅ Add docstrings and comments
✅ Test migrations before applying
✅ Lock database rows during critical operations
✅ Validate input on both frontend and backend
✅ Handle errors gracefully
✅ Log important operations
✅ Keep frontend and backend types in sync

### DON'T
❌ Edit applied migrations
❌ Skip transaction locking for concurrent operations
❌ Trust client-side validation alone
❌ Return sensitive data to unauthorized users
❌ Use floating-point math for financial calculations (use Decimal)
❌ Hard-code configuration (use environment variables)
❌ Commit without testing locally first

---

**Note:** This document evolves with the project. Update it when architectural decisions change.

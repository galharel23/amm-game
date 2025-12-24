# AMM Game - Database Schema Design

## Overview

This database supports a blockchain financial experiment platform where:
- Admins create and manage experiments
- Players participate in AMM trading experiments
- Each experiment has multiple rounds with multiple groups
- Players see limited price information (one currency only)
- Real-time concurrent trading with transaction locking

## Entity Relationship Overview

```
Experiment (1) ──→ (M) Round ──→ (M) ExperimentRound
    │                                      │
    │                                      ├──→ (M) Transaction
    │                                      ├──→ (M) PlayerCurrencyKnowledge
    │                                      ├──→ (M) UserFeedback
    │                                      └──→ (M) PlayerBalance
    └──→ (M) Group ──→ (M) PlayerUser
```

## Tables

### 1. User (Base Table)
Base table for all users using joined table inheritance.

**Fields:**
- `id` - UUID, Primary Key
- `username` - String, Unique, Not Null
- `user_type` - Enum (ADMIN, PLAYER), Not Null
- `created_at` - DateTime, Not Null
- `updated_at` - DateTime, Not Null

### 2. AdminUser
Admin users who create and manage experiments.

**Fields:**
- `id` - UUID, Primary Key, Foreign Key → User.id

### 3. PlayerUser
Players who participate in experiments.

**Fields:**
- `id` - UUID, Primary Key, Foreign Key → User.id
- `group_id` - UUID, Foreign Key → Group.id, Nullable
- `payment_amount_ils` - Decimal(10,2), Nullable

### 4. Currency
Trading currencies used in experiments.

**Fields:**
- `id` - UUID, Primary Key
- `symbol` - String(10), Unique, Not Null
- `name_en` - String(100), Not Null
- `name_he` - String(100), Not Null
- `image_url` - String(500), Nullable
- `created_at` - DateTime, Not Null

### 5. Experiment
Experiment definition and configuration.

**Fields:**
- `id` - UUID, Primary Key
- `name` - String(200), Not Null
- `admin_id` - UUID, Foreign Key → AdminUser.id, Not Null
- `num_rounds` - Integer, Not Null
- `num_training_rounds` - Integer, Not Null
- `num_rounds_for_payment` - Integer, Not Null
- `num_players` - Integer, Not Null
- `num_groups` - Integer, Not Null
- `created_at` - DateTime, Not Null
- `started_at` - DateTime, Nullable
- `ended_at` - DateTime, Nullable

### 6. Group
Player groups within an experiment.

**Fields:**
- `id` - UUID, Primary Key
- `experiment_id` - UUID, Foreign Key → Experiment.id, Not Null
- `group_number` - Integer, Not Null
- `created_at` - DateTime, Not Null

### 7. Round
Logical round definition (applies to all groups).

**Fields:**
- `id` - UUID, Primary Key
- `experiment_id` - UUID, Foreign Key → Experiment.id, Not Null
- `round_number` - Integer, Not Null
- `is_training_round` - Boolean, Not Null
- `counts_for_payment` - Boolean, Not Null
- `duration_minutes` - Integer, Not Null
- `currency_x_id` - UUID, Foreign Key → Currency.id, Not Null
- `currency_y_id` - UUID, Foreign Key → Currency.id, Not Null
- `external_price_x` - Decimal(20,8), Not Null
- `external_price_y` - Decimal(20,8), Not Null
- `initial_reserve_x` - Decimal(20,8), Not Null
- `initial_reserve_y` - Decimal(20,8), Not Null
- `created_at` - DateTime, Not Null
- `started_at` - DateTime, Nullable
- `ended_at` - DateTime, Nullable

### 8. ExperimentRound
Actual AMM pool instance for a specific group in a round.

**Fields:**
- `id` - UUID, Primary Key
- `round_id` - UUID, Foreign Key → Round.id, Not Null
- `group_id` - UUID, Foreign Key → Group.id, Not Null
- `reserve_x` - Decimal(20,8), Not Null
- `reserve_y` - Decimal(20,8), Not Null
- `k_constant` - Decimal(40,16), Not Null
- `transaction_fee_percent` - Decimal(5,2), Not Null, Default 0
- `is_active` - Boolean, Not Null, Default False
- `started_at` - DateTime, Nullable
- `ended_at` - DateTime, Nullable
- `created_at` - DateTime, Not Null

### 9. PlayerCurrencyKnowledge
Tracks which currency price each player can see.

**Fields:**
- `id` - UUID, Primary Key
- `player_id` - UUID, Foreign Key → PlayerUser.id, Not Null
- `experiment_round_id` - UUID, Foreign Key → ExperimentRound.id, Not Null
- `revealed_currency_id` - UUID, Foreign Key → Currency.id, Not Null
- `created_at` - DateTime, Not Null

### 10. PlayerBalance
Tracks currency holdings for each player in each experiment round.

**Fields:**
- `id` - UUID, Primary Key
- `player_id` - UUID, Foreign Key → PlayerUser.id, Not Null
- `experiment_round_id` - UUID, Foreign Key → ExperimentRound.id, Not Null
- `currency_id` - UUID, Foreign Key → Currency.id, Not Null
- `balance` - Decimal(20,8), Not Null, Default 0
- `updated_at` - DateTime, Not Null

### 11. Transaction
Record of all swap transactions.

**Fields:**
- `id` - UUID, Primary Key
- `experiment_round_id` - UUID, Foreign Key → ExperimentRound.id, Not Null
- `player_id` - UUID, Foreign Key → PlayerUser.id, Not Null
- `currency_in_id` - UUID, Foreign Key → Currency.id, Not Null
- `amount_in` - Decimal(20,8), Not Null
- `currency_out_id` - UUID, Foreign Key → Currency.id, Not Null
- `amount_out` - Decimal(20,8), Not Null
- `price_ratio` - Decimal(20,8), Not Null
- `has_completed` - Boolean, Not Null, Default True
- `created_at` - DateTime, Not Null

### 12. UserFeedback
Auto-generated feedback for players at end of each round.

**Fields:**
- `id` - UUID, Primary Key
- `player_id` - UUID, Foreign Key → PlayerUser.id, Not Null
- `experiment_round_id` - UUID, Foreign Key → ExperimentRound.id, Not Null
- `feedback_items` - JSON, Not Null
- `created_at` - DateTime, Not Null

## Implementation Notes

- Use UUID for all primary keys
- Use Decimal for financial data (no floats)
- Implement row-level locking for concurrent transactions
- Index foreign keys and frequently queried fields
- Validate constraints at both database and application level

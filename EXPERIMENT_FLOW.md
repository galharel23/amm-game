# Experiment Flow - Complete Lifecycle

This document describes the complete lifecycle of an experiment in the AMM Game platform, from creation to completion and payment.

---

## Overview

An experiment is a controlled environment where players trade in AMM pools while having limited information (each player sees the price of only one currency). The system tracks all actions, provides feedback, and calculates payments based on performance.

---

## Phase 1: Experiment Setup (Admin)

### 1.1 Create Experiment
**Who:** Admin  
**Action:** Admin creates a new experiment

**Data Created:**
- `Experiment` record with:
  - name
  - num_rounds (e.g., 10 total rounds)
  - num_training_rounds (e.g., 3 training rounds)
  - num_rounds_for_payment (e.g., 3 rounds to count for payment)
  - num_players (e.g., 16 players)
  - num_groups (e.g., 2 groups)

**Business Logic:**
- Training rounds don't count for payment
- Real rounds = num_rounds - num_training_rounds (e.g., 7 real rounds)
- Payment calculated from randomly selected rounds (num_rounds_for_payment out of real rounds)

### 1.2 Create Groups
**Who:** System (automatic)  
**When:** After experiment creation

**Data Created:**
- `Group` records (one per group)
  - group_number: 1, 2, 3...
  - experiment_id: links to experiment

**Result:**
- If num_groups = 2 and num_players = 16, each group will have 8 players

### 1.3 Configure Rounds
**Who:** Admin  
**Action:** Admin creates and configures each round

**Data Created (per round):**
- `Round` record with:
  - round_number (1, 2, 3...)
  - is_training_round (true for first 3, false for rest)
  - counts_for_payment (randomly selected from real rounds)
  - duration_minutes (e.g., 5 minutes)
  - currency_x_id (e.g., BTC)
  - currency_y_id (e.g., ETH)
  - external_price_x (e.g., 45000 ILS - "real" market price)
  - external_price_y (e.g., 3000 ILS - "real" market price)
  - initial_reserve_x (e.g., 100 BTC)
  - initial_reserve_y (e.g., 1500 ETH)

**Key Points:**
- All groups in same round use the same currency pair
- All groups start with same initial reserves
- External prices are in "third universal currency" (ILS)
- Admin can set different currencies for each round

---

## Phase 2: Player Assignment

### 2.1 Players Join
**Who:** Players  
**Action:** Players register/are assigned to experiment

**Data Created:**
- `PlayerUser` records created if new players
- Players remain unassigned (group_id = NULL)

### 2.2 Start Experiment - Assign Groups
**Who:** Admin  
**Action:** Admin clicks "Start Experiment"

**Business Logic:**
- System assigns players evenly to groups
- Updates PlayerUser.group_id for each player
- Sets Experiment.started_at timestamp

**Result:**
- Each player now belongs to a specific group
- Group assignment is permanent for entire experiment

---

## Phase 3: Round Initialization

### For Each Round (Sequential):

### 3.1 Create Experiment Rounds (Pools)
**Who:** System (automatic)  
**When:** Round starts

**Data Created (one per group):**
- `ExperimentRound` records:
  - round_id: links to Round
  - group_id: links to Group
  - reserve_x: copied from Round.initial_reserve_x
  - reserve_y: copied from Round.initial_reserve_y
  - k_constant: reserve_x * reserve_y
  - transaction_fee_percent: 0 (default)
  - is_active: false (will be set to true when round starts)

**Result:**
- If 2 groups, creates 2 ExperimentRounds (pools), one per group
- Each group has its own isolated pool

### 3.2 Initialize Player Balances
**Who:** System (automatic)

**Data Created (per player, per currency):**
- `PlayerBalance` records:
  - player_id
  - experiment_round_id
  - currency_id: BTC
  - balance: 10 BTC (starting balance)
  
- `PlayerBalance` records:
  - player_id
  - experiment_round_id
  - currency_id: ETH
  - balance: 150 ETH (starting balance)

**Key Points:**
- Each player gets starting balance of both currencies
- Balances are specific to this round (new balances each round)

### 3.3 Assign Currency Knowledge
**Who:** System (automatic - random assignment)

**Data Created (one per player):**
- `PlayerCurrencyKnowledge` record:
  - player_id
  - experiment_round_id
  - revealed_currency_id: RANDOMLY either currency_x_id OR currency_y_id

**Business Logic:**
- Each player can see price of ONE currency only
- Random 50/50 split within each group
- Example: Player sees "BTC = 45,000 ILS" but NOT the ETH price

### 3.4 Activate Round
**Who:** System

**Updates:**
- Set ExperimentRound.is_active = true
- Set ExperimentRound.started_at = now()
- Set Round.started_at = now()

**Result:**
- Players can now start trading
- Timer starts (duration_minutes)

---

## Phase 4: Active Trading

### 4.1 Player Views Round
**Who:** Player  
**UI Shows:**
- Their assigned pool (ExperimentRound for their group)
- Current reserves (reserve_x, reserve_y)
- Their balances (from PlayerBalance)
- Price of ONE currency (from PlayerCurrencyKnowledge + Round.external_price)
- Current AMM price (calculated from reserves: price_y/price_x)
- Time remaining

**What Player DOESN'T See:**
- Other currency's external price
- Other groups' pools
- Other players' actions (unless real-time updates implemented)

### 4.2 Execute Swap
**Who:** Player  
**Action:** Player swaps currency X for currency Y

**Transaction Flow (with Locking):**

```
BEGIN TRANSACTION

1. LOCK ROWS (to prevent concurrent conflicts)
   - SELECT * FROM experiment_round WHERE id = ? FOR UPDATE
   - SELECT * FROM player_balance WHERE player_id = ? AND experiment_round_id = ? FOR UPDATE

2. VALIDATE
   - Pool is active (ExperimentRound.is_active = true)
   - Player has sufficient balance (PlayerBalance.balance >= amount_in)
   - Pool has sufficient liquidity (reserve_out > amount_out_calculated)

3. CALCULATE OUTPUT (AMM Formula)
   input_with_fee = amount_in * (1 - transaction_fee_percent / 100)
   amount_out = (reserve_y * input_with_fee) / (reserve_x + input_with_fee)

4. UPDATE RESERVES
   UPDATE experiment_round SET
     reserve_x = reserve_x + amount_in,
     reserve_y = reserve_y - amount_out,
     k_constant = new_reserve_x * new_reserve_y

5. UPDATE BALANCES
   UPDATE player_balance SET balance = balance - amount_in 
     WHERE player_id = ? AND currency_id = currency_in_id
   
   UPDATE player_balance SET balance = balance + amount_out
     WHERE player_id = ? AND currency_id = currency_out_id

6. CREATE TRANSACTION RECORD
   INSERT INTO transaction (
     experiment_round_id, player_id,
     currency_in_id, amount_in,
     currency_out_id, amount_out,
     price_ratio, has_completed, created_at
   )

COMMIT TRANSACTION
```

**Key Points:**
- Row-level locking prevents race conditions
- Reserves update atomically
- All or nothing - if any step fails, entire transaction rolls back

### 4.3 Multiple Players Trading Concurrently
**What Happens:**
- Database locks ensure one transaction completes before next
- Reserves change after each swap
- Price changes with each swap (constant product formula)
- Players see updated reserves after each swap

---

## Phase 5: Round Completion

### 5.1 Time Expires
**Who:** System (automatic)  
**When:** duration_minutes elapsed

**Updates:**
- Set ExperimentRound.is_active = false
- Set ExperimentRound.ended_at = now()
- Set Round.ended_at = now()

**Result:**
- No more trading allowed in this round
- Reserves frozen

### 5.2 Generate Feedback
**Who:** System (automatic)  
**Action:** Analyze each player's performance

**Data Created (per player):**
- `UserFeedback` record:
  - player_id
  - experiment_round_id
  - feedback_items: JSON array of strings

**Feedback Content (auto-generated):**
```json
{
  "feedback_items": [
    "You completed 3 swaps this round",
    "Good timing on swap #2 - you bought low",
    "Swap #1 could have been better - price moved against you",
    "Overall profit: +5% compared to starting position",
    "You ranked 4th out of 8 in your group"
  ]
}
```

**Business Logic:**
- Compare final balances to starting balances
- Calculate profit/loss in ILS terms using external prices
- Identify good vs bad trades based on price movements
- Rank players within group

### 5.3 Players View Feedback
**Who:** Player  
**UI Shows:**
- Feedback summary
- Final balances
- Comparison to other players (aggregate/ranking)
- What the "real" prices were (both currencies revealed)

---

## Phase 6: Next Round or End Experiment

### 6.1 More Rounds Remaining
**Action:** System proceeds to Phase 3 with next round
- New currencies may be selected
- New initial reserves
- New random currency knowledge assignment
- New player balances (previous round balances don't carry over)

### 6.2 All Rounds Complete
**Action:** Experiment ends - proceed to Phase 7

---

## Phase 7: Experiment Completion & Payment

### 7.1 Mark Experiment Complete
**Who:** System (automatic after last round)

**Updates:**
- Set Experiment.ended_at = now()

### 7.2 Calculate Payments
**Who:** System (automatic or admin-triggered)

**Business Logic:**

```
For each player:

1. GET PAYMENT ROUNDS
   - SELECT rounds WHERE experiment_id = ? AND counts_for_payment = true

2. CALCULATE PERFORMANCE PER ROUND
   For each payment round:
     - Get player's final balances (PlayerBalance)
     - Convert to ILS using external prices:
       value_ils = (balance_x * external_price_x) + (balance_y * external_price_y)
     - Compare to starting value
     - profit_round = final_value - starting_value

3. AGGREGATE PERFORMANCE
   total_profit = SUM(profit_round for all payment rounds)
   
4. CONVERT TO PAYMENT
   - Apply payment formula (e.g., base_payment + performance_bonus)
   - Example: 50 ILS base + (total_profit * 0.1)

5. STORE PAYMENT
   UPDATE player_user SET payment_amount_ils = calculated_payment
```

**Key Points:**
- Only rounds with counts_for_payment = true are used
- Training rounds never count
- Payment based on performance in ILS terms
- Stored in PlayerUser.payment_amount_ils

### 7.3 Admin Reviews & Processes Payments
**Who:** Admin

**Actions:**
- View payment summary for all players
- Export payment data
- Process actual payments to players
- Close experiment

---

## Data Flow Summary

```
Experiment Created
  ↓
Groups Created (automatic)
  ↓
Rounds Configured (admin)
  ↓
Players Assigned to Groups (admin starts)
  ↓
FOR EACH ROUND:
  ↓
  ExperimentRounds Created (one per group)
  ↓
  Player Balances Initialized
  ↓
  Currency Knowledge Assigned (random)
  ↓
  Round Activated
  ↓
  Players Trade (concurrent with locking)
  ↓
  Round Ends (timer expires)
  ↓
  Feedback Generated
  ↓
  [Next Round or End]
  ↓
Experiment Ends
  ↓
Payments Calculated (based on selected rounds)
  ↓
Admin Processes Payments
```

---

## Key Design Principles

### 1. Information Asymmetry
- Each player sees only ONE currency's external price
- Forces players to use AMM price discovery
- Tests understanding of constant product formula

### 2. Group Isolation
- Each group has independent pool
- Same initial conditions, but different outcomes
- Enables comparison between groups

### 3. Concurrent Safety
- Database locking prevents race conditions
- Atomic transactions ensure consistency
- Reserves always match k_constant

### 4. Flexible Configuration
- Admin controls all parameters
- Different currencies per round
- Different reserve ratios
- Different payment structures

### 5. Fair Payment
- Randomly selected rounds prevent gaming
- Based on ILS value (not token counts)
- Training rounds allow learning without risk

---

## Real-Time Updates (Future)

When WebSocket implemented:

**Events to Broadcast:**
- `pool_updated` - Reserves changed (after each swap)
- `swap_executed` - Someone traded (aggregate, not individual)
- `time_remaining` - Countdown updates
- `round_ended` - Round completed
- `feedback_ready` - Personal feedback available

**Admin Dashboard Events:**
- `player_action` - Real-time activity monitoring
- `group_stats` - Aggregate statistics per group
- `experiment_progress` - Overall experiment status

---

## Example: Complete Experiment

**Setup:**
- 2 groups, 8 players per group (16 total)
- 5 rounds total: 2 training, 3 real
- 2 of the 3 real rounds count for payment (random selection)
- Each round: 5 minutes duration

**Timeline:**

1. **Day 1 - Setup**
   - Admin creates experiment
   - Admin configures 5 rounds with different currency pairs
   - Admin assigns 16 players to 2 groups (8 each)

2. **Day 2 - Training Rounds**
   - Round 1 (Training): BTC/ETH - Players learn mechanics
   - Round 2 (Training): USD/EUR - Players practice
   - Feedback provided, no payment impact

3. **Day 3 - Real Rounds**
   - Round 3 (Real, Counts): DAI/USDC - Stablecoin trading
   - Round 4 (Real, Counts): BTC/DAI - Volatile vs stable
   - Round 5 (Real, No count): ETH/USD - Final round

4. **After Experiment**
   - System calculates performance in rounds 3 & 4 only
   - Player A: +15% in round 3, +8% in round 4 → High payment
   - Player B: -5% in round 3, +2% in round 4 → Lower payment
   - Admin reviews and processes payments

**Result:**
- Players learned AMM mechanics
- Performance measured objectively
- Payments fair and transparent
- Data collected for research analysis

---

## Technical Notes

### Database Consistency
- Use transactions for all multi-step operations
- Lock order: ExperimentRound → PlayerBalance (by currency_id)
- Validate before commit
- Log all errors for debugging

### Performance Optimization
- Index on is_active for quick pool lookup
- Index on created_at for time-series queries
- Composite index on (experiment_round_id, player_id) for balance queries
- Cache external prices (don't recalculate)

### Monitoring
- Track transaction success rate
- Monitor lock wait times
- Alert on stuck rounds (past duration + buffer)
- Log all admin actions

---

This document provides the complete flow of how experiments are managed in the AMM Game platform.

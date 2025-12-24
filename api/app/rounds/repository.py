# app/rounds/repository.py

from __future__ import annotations

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Round, ExperimentRound, Experiment, Group, Currency, PlayerBalance, PlayerCurrencyKnowledge


class RoundNotFoundError(Exception):
    """Raised when a round is not found."""
    pass


class ExperimentRoundNotFoundError(Exception):
    """Raised when an experiment round is not found."""
    pass


def get_round_by_id(db: Session, round_id: UUID) -> Optional[Round]:
    """Get a round by ID."""
    return db.query(Round).filter(Round.id == round_id).first()


def get_rounds_by_experiment(db: Session, experiment_id: UUID) -> list[Round]:
    """Get all rounds for an experiment."""
    return (
        db.query(Round)
        .filter(Round.experiment_id == experiment_id)
        .order_by(Round.round_number)
        .all()
    )


def create_round(
    db: Session,
    experiment_id: UUID,
    round_number: int,
    is_training_round: bool,
    counts_for_payment: bool,
    duration_minutes: int,
    currency_x_id: UUID,
    currency_y_id: UUID,
    external_price_x: float,
    external_price_y: float,
    initial_reserve_x: float,
    initial_reserve_y: float,
) -> Round:
    """Create a new round configuration."""
    # Verify experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise ValueError(f"Experiment {experiment_id} not found")
    
    # Verify currencies exist
    currency_x = db.query(Currency).filter(Currency.id == currency_x_id).first()
    currency_y = db.query(Currency).filter(Currency.id == currency_y_id).first()
    if not currency_x or not currency_y:
        raise ValueError("Invalid currency IDs")
    
    round_obj = Round(
        experiment_id=experiment_id,
        round_number=round_number,
        is_training_round=is_training_round,
        counts_for_payment=counts_for_payment,
        duration_minutes=duration_minutes,
        currency_x_id=currency_x_id,
        currency_y_id=currency_y_id,
        external_price_x=Decimal(str(external_price_x)),
        external_price_y=Decimal(str(external_price_y)),
        initial_reserve_x=Decimal(str(initial_reserve_x)),
        initial_reserve_y=Decimal(str(initial_reserve_y)),
    )
    
    db.add(round_obj)
    db.commit()
    db.refresh(round_obj)
    return round_obj


def initialize_experiment_rounds(db: Session, round_id: UUID) -> list[ExperimentRound]:
    """Initialize experiment rounds (pool instances) for all groups when a round starts.
    
    This creates one ExperimentRound per group, each with its own reserves.
    """
    round_obj = get_round_by_id(db, round_id)
    if not round_obj:
        raise RoundNotFoundError(f"Round {round_id} not found")
    
    # Get all groups for this experiment
    groups = db.query(Group).filter(Group.experiment_id == round_obj.experiment_id).all()
    
    experiment_rounds = []
    for group in groups:
        # Calculate k_constant
        k_constant = round_obj.initial_reserve_x * round_obj.initial_reserve_y
        
        exp_round = ExperimentRound(
            round_id=round_id,
            group_id=group.id,
            reserve_x=round_obj.initial_reserve_x,
            reserve_y=round_obj.initial_reserve_y,
            k_constant=k_constant,
            transaction_fee_percent=Decimal("0"),  # Default 0% fee
            is_active=False,  # Will be activated when round starts
        )
        db.add(exp_round)
        experiment_rounds.append(exp_round)
    
    db.commit()
    for exp_round in experiment_rounds:
        db.refresh(exp_round)
    
    return experiment_rounds


def start_round(db: Session, round_id: UUID) -> Round:
    """Start a round - activate all experiment rounds and initialize player balances."""
    round_obj = get_round_by_id(db, round_id)
    if not round_obj:
        raise RoundNotFoundError(f"Round {round_id} not found")
    
    if round_obj.started_at:
        raise ValueError("Round has already been started")
    
    # Mark round as started
    round_obj.started_at = datetime.now(timezone.utc)
    
    # Get all experiment rounds for this round
    experiment_rounds = (
        db.query(ExperimentRound)
        .filter(ExperimentRound.round_id == round_id)
        .all()
    )
    
    # Activate all experiment rounds and set started_at
    for exp_round in experiment_rounds:
        exp_round.is_active = True
        exp_round.started_at = datetime.now(timezone.utc)
    
    # TODO: Initialize player balances and currency knowledge
    # This would involve:
    # 1. Get all players in each group
    # 2. Create PlayerBalance for each player/currency/experiment_round
    # 3. Create PlayerCurrencyKnowledge (random assignment)
    
    db.commit()
    db.refresh(round_obj)
    return round_obj


def end_round(db: Session, round_id: UUID) -> Round:
    """End a round - deactivate all experiment rounds."""
    round_obj = get_round_by_id(db, round_id)
    if not round_obj:
        raise RoundNotFoundError(f"Round {round_id} not found")
    
    if not round_obj.started_at:
        raise ValueError("Cannot end a round that hasn't started")
    
    if round_obj.ended_at:
        raise ValueError("Round has already ended")
    
    # Mark round as ended
    round_obj.ended_at = datetime.now(timezone.utc)
    
    # Get all experiment rounds for this round
    experiment_rounds = (
        db.query(ExperimentRound)
        .filter(ExperimentRound.round_id == round_id)
        .all()
    )
    
    # Deactivate all experiment rounds and set ended_at
    for exp_round in experiment_rounds:
        exp_round.is_active = False
        exp_round.ended_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(round_obj)
    return round_obj


def get_experiment_round_by_id(db: Session, experiment_round_id: UUID) -> Optional[ExperimentRound]:
    """Get an experiment round by ID."""
    return db.query(ExperimentRound).filter(ExperimentRound.id == experiment_round_id).first()


def get_experiment_rounds_by_round(db: Session, round_id: UUID) -> list[ExperimentRound]:
    """Get all experiment rounds (pool instances) for a round."""
    return db.query(ExperimentRound).filter(ExperimentRound.round_id == round_id).all()


def get_experiment_round_by_group(db: Session, round_id: UUID, group_id: UUID) -> Optional[ExperimentRound]:
    """Get the experiment round for a specific group in a specific round."""
    return (
        db.query(ExperimentRound)
        .filter(ExperimentRound.round_id == round_id, ExperimentRound.group_id == group_id)
        .first()
    )


def update_round(db: Session, round_id: UUID, **update_data) -> Round:
    """Update a round configuration."""
    round_obj = get_round_by_id(db, round_id)
    if not round_obj:
        raise RoundNotFoundError(f"Round {round_id} not found")
    
    # Update only provided fields
    for field, value in update_data.items():
        if value is not None and hasattr(round_obj, field):
            # Convert floats to Decimal for numeric fields
            if field in ['external_price_x', 'external_price_y', 'initial_reserve_x', 'initial_reserve_y']:
                value = Decimal(str(value))
            setattr(round_obj, field, value)
    
    db.commit()
    db.refresh(round_obj)
    return round_obj


def delete_round(db: Session, round_id: UUID) -> bool:
    """Delete a round."""
    round_obj = get_round_by_id(db, round_id)
    if not round_obj:
        raise RoundNotFoundError(f"Round {round_id} not found")
    
    db.delete(round_obj)
    db.commit()
    return True

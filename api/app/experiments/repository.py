# app/experiments/repository.py

from __future__ import annotations

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Experiment, Group, AdminUser


class ExperimentNotFoundError(Exception):
    """Raised when an experiment is not found."""
    pass


class GroupNotFoundError(Exception):
    """Raised when a group is not found."""
    pass


class InvalidAdminError(Exception):
    """Raised when the user is not an admin."""
    pass


def get_experiment_by_id(db: Session, experiment_id: UUID) -> Optional[Experiment]:
    """Get an experiment by ID."""
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()


def get_all_experiments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    created_by_id: Optional[UUID] = None,
) -> list[Experiment]:
    """Get all experiments with optional filtering by creator."""
    query = db.query(Experiment)
    
    if created_by_id:
        query = query.filter(Experiment.created_by_id == created_by_id)
    
    return query.offset(skip).limit(limit).all()


def create_experiment(
    db: Session,
    name: str,
    num_rounds: int,
    num_training_rounds: int,
    num_rounds_for_payment: int,
    num_players: int,
    num_groups: int,
    created_by_id: UUID,
) -> Experiment:
    """Create a new experiment and its groups."""
    # Verify the creator is an admin
    admin = db.query(AdminUser).filter(AdminUser.id == created_by_id).first()
    if not admin:
        raise InvalidAdminError(f"User {created_by_id} is not an admin")
    
    # Create experiment
    experiment = Experiment(
        name=name,
        num_rounds=num_rounds,
        num_training_rounds=num_training_rounds,
        num_rounds_for_payment=num_rounds_for_payment,
        num_players=num_players,
        num_groups=num_groups,
        created_by_id=created_by_id,
    )
    
    db.add(experiment)
    db.flush()  # Get the experiment ID
    
    # Automatically create groups for this experiment
    for group_num in range(1, num_groups + 1):
        group = Group(
            experiment_id=experiment.id,
            group_number=group_num,
        )
        db.add(group)
    
    db.commit()
    db.refresh(experiment)
    return experiment


def update_experiment(
    db: Session,
    experiment_id: UUID,
    **update_data,
) -> Experiment:
    """Update an experiment."""
    experiment = get_experiment_by_id(db, experiment_id)
    if not experiment:
        raise ExperimentNotFoundError(f"Experiment {experiment_id} not found")
    
    # Update only provided fields
    for field, value in update_data.items():
        if value is not None and hasattr(experiment, field):
            setattr(experiment, field, value)
    
    db.commit()
    db.refresh(experiment)
    return experiment


def start_experiment(db: Session, experiment_id: UUID) -> Experiment:
    """Mark an experiment as started."""
    experiment = get_experiment_by_id(db, experiment_id)
    if not experiment:
        raise ExperimentNotFoundError(f"Experiment {experiment_id} not found")
    
    if experiment.started_at:
        raise ValueError("Experiment has already been started")
    
    experiment.started_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(experiment)
    return experiment


def end_experiment(db: Session, experiment_id: UUID) -> Experiment:
    """Mark an experiment as ended."""
    experiment = get_experiment_by_id(db, experiment_id)
    if not experiment:
        raise ExperimentNotFoundError(f"Experiment {experiment_id} not found")
    
    if not experiment.started_at:
        raise ValueError("Cannot end an experiment that hasn't started")
    
    if experiment.ended_at:
        raise ValueError("Experiment has already ended")
    
    experiment.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(experiment)
    return experiment


def delete_experiment(db: Session, experiment_id: UUID) -> bool:
    """Delete an experiment and all related data."""
    experiment = get_experiment_by_id(db, experiment_id)
    if not experiment:
        raise ExperimentNotFoundError(f"Experiment {experiment_id} not found")
    
    db.delete(experiment)
    db.commit()
    return True


def get_groups_by_experiment(db: Session, experiment_id: UUID) -> list[Group]:
    """Get all groups for an experiment."""
    return db.query(Group).filter(Group.experiment_id == experiment_id).all()


def get_group_by_id(db: Session, group_id: UUID) -> Optional[Group]:
    """Get a group by ID."""
    return db.query(Group).filter(Group.id == group_id).first()

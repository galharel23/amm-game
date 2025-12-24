# app/rounds/routes.py

from __future__ import annotations

from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from .schemas import (
    RoundCreate,
    RoundUpdate,
    RoundResponse,
    ExperimentRoundResponse,
    RoundListResponse,
    ErrorResponse,
)
from .repository import (
    create_round as repo_create_round,
    get_round_by_id,
    get_rounds_by_experiment,
    initialize_experiment_rounds as repo_initialize_experiment_rounds,
    start_round as repo_start_round,
    end_round as repo_end_round,
    get_experiment_rounds_by_round,
    get_experiment_round_by_group,
    update_round as repo_update_round,
    delete_round as repo_delete_round,
    RoundNotFoundError,
)
from app.database import get_db

router = APIRouter()


# -------------------- Routes -------------------- #

@router.post(
    "/",
    response_model=RoundResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def create_round(
    round_data: RoundCreate,
    db: Session = Depends(get_db),
):
    """Create a new round configuration for an experiment."""
    try:
        round_obj = repo_create_round(
            db=db,
            experiment_id=round_data.experiment_id,
            round_number=round_data.round_number,
            is_training_round=round_data.is_training_round,
            counts_for_payment=round_data.counts_for_payment,
            duration_minutes=round_data.duration_minutes,
            currency_x_id=round_data.currency_x_id,
            currency_y_id=round_data.currency_y_id,
            external_price_x=round_data.external_price_x,
            external_price_y=round_data.external_price_y,
            initial_reserve_x=round_data.initial_reserve_x,
            initial_reserve_y=round_data.initial_reserve_y,
        )
        return RoundResponse.model_validate(round_obj)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create round: {str(e)}",
        )


@router.get(
    "/experiment/{experiment_id}",
    response_model=RoundListResponse,
)
def list_rounds_for_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """List all rounds for an experiment."""
    try:
        rounds = get_rounds_by_experiment(db, experiment_id)
        return RoundListResponse(
            rounds=[RoundResponse.model_validate(r) for r in rounds],
            total=len(rounds),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rounds: {str(e)}",
        )


@router.get(
    "/{round_id}",
    response_model=RoundResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_round(
    round_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a round by ID."""
    try:
        round_obj = get_round_by_id(db, round_id)
        if not round_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Round {round_id} not found",
            )
        return RoundResponse.model_validate(round_obj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get round: {str(e)}",
        )


@router.post(
    "/{round_id}/initialize",
    response_model=List[ExperimentRoundResponse],
    responses={404: {"model": ErrorResponse}},
)
def initialize_round_pools(
    round_id: UUID,
    db: Session = Depends(get_db),
):
    """Initialize experiment rounds (pool instances) for all groups.
    
    This creates one pool per group with the initial reserves from the round configuration.
    Call this before starting the round.
    """
    try:
        experiment_rounds = repo_initialize_experiment_rounds(db, round_id)
        return [ExperimentRoundResponse.model_validate(er) for er in experiment_rounds]
    
    except RoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize round pools: {str(e)}",
        )


@router.post(
    "/{round_id}/start",
    response_model=RoundResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
def start_round(
    round_id: UUID,
    db: Session = Depends(get_db),
):
    """Start a round (activate all pools and initialize player balances)."""
    try:
        round_obj = repo_start_round(db, round_id)
        return RoundResponse.model_validate(round_obj)
    
    except RoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start round: {str(e)}",
        )


@router.post(
    "/{round_id}/end",
    response_model=RoundResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
def end_round(
    round_id: UUID,
    db: Session = Depends(get_db),
):
    """End a round (deactivate all pools)."""
    try:
        round_obj = repo_end_round(db, round_id)
        return RoundResponse.model_validate(round_obj)
    
    except RoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end round: {str(e)}",
        )


@router.get(
    "/{round_id}/pools",
    response_model=List[ExperimentRoundResponse],
    responses={404: {"model": ErrorResponse}},
)
def list_round_pools(
    round_id: UUID,
    db: Session = Depends(get_db),
):
    """List all experiment rounds (pool instances) for a round."""
    try:
        # Verify round exists
        round_obj = get_round_by_id(db, round_id)
        if not round_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Round {round_id} not found",
            )
        
        experiment_rounds = get_experiment_rounds_by_round(db, round_id)
        return [ExperimentRoundResponse.model_validate(er) for er in experiment_rounds]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list round pools: {str(e)}",
        )


@router.get(
    "/{round_id}/pools/group/{group_id}",
    response_model=ExperimentRoundResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_group_pool(
    round_id: UUID,
    group_id: UUID,
    db: Session = Depends(get_db),
):
    """Get the pool (experiment round) for a specific group in a round."""
    try:
        experiment_round = get_experiment_round_by_group(db, round_id, group_id)
        if not experiment_round:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pool for group {group_id} in round {round_id} not found",
            )
        return ExperimentRoundResponse.model_validate(experiment_round)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get group pool: {str(e)}",
        )


@router.patch(
    "/{round_id}",
    response_model=RoundResponse,
    responses={404: {"model": ErrorResponse}},
)
def update_round(
    round_id: UUID,
    round_data: RoundUpdate,
    db: Session = Depends(get_db),
):
    """Update a round configuration."""
    try:
        update_dict = round_data.model_dump(exclude_unset=True)
        round_obj = repo_update_round(db, round_id, **update_dict)
        return RoundResponse.model_validate(round_obj)
    
    except RoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update round: {str(e)}",
        )


@router.delete(
    "/{round_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_round(
    round_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a round."""
    try:
        repo_delete_round(db, round_id)
        return None
    
    except RoundNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete round: {str(e)}",
        )

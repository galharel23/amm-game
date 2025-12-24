# app/experiments/routes.py

from __future__ import annotations

from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from .schemas import (
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentResponse,
    ExperimentWithGroups,
    ExperimentListResponse,
    GroupResponse,
    ErrorResponse,
)
from .repository import (
    create_experiment as repo_create_experiment,
    get_experiment_by_id,
    get_all_experiments,
    update_experiment as repo_update_experiment,
    start_experiment as repo_start_experiment,
    end_experiment as repo_end_experiment,
    delete_experiment as repo_delete_experiment,
    get_groups_by_experiment,
    ExperimentNotFoundError,
    InvalidAdminError,
)
from app.database import get_db

router = APIRouter()


# -------------------- Routes -------------------- #

@router.post(
    "/",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
)
def create_experiment(
    experiment_data: ExperimentCreate,
    created_by_id: UUID,  # TODO: Get from JWT token in real implementation
    db: Session = Depends(get_db),
):
    """Create a new experiment with groups.
    
    This will automatically create the specified number of groups.
    
    TODO: Replace created_by_id parameter with JWT authentication.
    """
    try:
        experiment = repo_create_experiment(
            db=db,
            name=experiment_data.name,
            num_rounds=experiment_data.num_rounds,
            num_training_rounds=experiment_data.num_training_rounds,
            num_rounds_for_payment=experiment_data.num_rounds_for_payment,
            num_players=experiment_data.num_players,
            num_groups=experiment_data.num_groups,
            created_by_id=created_by_id,
        )
        return ExperimentResponse.model_validate(experiment)
    
    except InvalidAdminError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create experiment: {str(e)}",
        )


@router.get(
    "/",
    response_model=ExperimentListResponse,
)
def list_experiments(
    skip: int = 0,
    limit: int = 100,
    created_by_id: UUID = None,  # Optional filter
    db: Session = Depends(get_db),
):
    """List all experiments with optional filtering."""
    try:
        experiments = get_all_experiments(
            db, skip=skip, limit=limit, created_by_id=created_by_id
        )
        return ExperimentListResponse(
            experiments=[ExperimentResponse.model_validate(e) for e in experiments],
            total=len(experiments),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list experiments: {str(e)}",
        )


@router.get(
    "/{experiment_id}",
    response_model=ExperimentResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """Get an experiment by ID."""
    try:
        experiment = get_experiment_by_id(db, experiment_id)
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Experiment {experiment_id} not found",
            )
        return ExperimentResponse.model_validate(experiment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get experiment: {str(e)}",
        )


@router.get(
    "/{experiment_id}/with-groups",
    response_model=ExperimentWithGroups,
    responses={404: {"model": ErrorResponse}},
)
def get_experiment_with_groups(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """Get an experiment with all its groups."""
    try:
        experiment = get_experiment_by_id(db, experiment_id)
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Experiment {experiment_id} not found",
            )
        
        groups = get_groups_by_experiment(db, experiment_id)
        
        return ExperimentWithGroups(
            **ExperimentResponse.model_validate(experiment).model_dump(),
            groups=[GroupResponse.model_validate(g) for g in groups],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get experiment with groups: {str(e)}",
        )


@router.patch(
    "/{experiment_id}",
    response_model=ExperimentResponse,
    responses={404: {"model": ErrorResponse}},
)
def update_experiment(
    experiment_id: UUID,
    experiment_data: ExperimentUpdate,
    db: Session = Depends(get_db),
):
    """Update an experiment."""
    try:
        # Only pass non-None values
        update_dict = experiment_data.model_dump(exclude_unset=True)
        
        experiment = repo_update_experiment(db, experiment_id, **update_dict)
        return ExperimentResponse.model_validate(experiment)
    
    except ExperimentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update experiment: {str(e)}",
        )


@router.post(
    "/{experiment_id}/start",
    response_model=ExperimentResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
def start_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """Start an experiment (set started_at timestamp)."""
    try:
        experiment = repo_start_experiment(db, experiment_id)
        return ExperimentResponse.model_validate(experiment)
    
    except ExperimentNotFoundError as e:
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
            detail=f"Failed to start experiment: {str(e)}",
        )


@router.post(
    "/{experiment_id}/end",
    response_model=ExperimentResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
def end_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """End an experiment (set ended_at timestamp)."""
    try:
        experiment = repo_end_experiment(db, experiment_id)
        return ExperimentResponse.model_validate(experiment)
    
    except ExperimentNotFoundError as e:
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
            detail=f"Failed to end experiment: {str(e)}",
        )


@router.delete(
    "/{experiment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_experiment(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete an experiment and all related data."""
    try:
        repo_delete_experiment(db, experiment_id)
        return None
    
    except ExperimentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete experiment: {str(e)}",
        )


@router.get(
    "/{experiment_id}/groups",
    response_model=List[GroupResponse],
    responses={404: {"model": ErrorResponse}},
)
def list_experiment_groups(
    experiment_id: UUID,
    db: Session = Depends(get_db),
):
    """List all groups for an experiment."""
    try:
        # Verify experiment exists
        experiment = get_experiment_by_id(db, experiment_id)
        if not experiment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Experiment {experiment_id} not found",
            )
        
        groups = get_groups_by_experiment(db, experiment_id)
        return [GroupResponse.model_validate(g) for g in groups]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list groups: {str(e)}",
        )

# app/users/routes.py

from __future__ import annotations

from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from .schemas import (
    UserRegister,
    UserLogin,
    UserBase,
    UserLoginResponse,
    AdminUserResponse,
    PlayerUserResponse,
    UserListResponse,
    PlayerAssignGroup,
    ErrorResponse,
)
from .repository import (
    create_user as repo_create_user,
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    get_all_players,
    update_player_group,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.database import get_db
from app.models.enums import UserType

router = APIRouter()


# -------------------- Helper Functions -------------------- #

def hash_password(password: str) -> str:
    """Hash a password. 
    
    TODO: Implement proper password hashing (bcrypt, argon2, etc.)
    For now, this is a placeholder.
    """
    # SECURITY WARNING: This is NOT secure! Use bcrypt or passlib in production
    return f"hashed_{password}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    TODO: Implement proper password verification.
    For now, this is a placeholder.
    """
    # SECURITY WARNING: This is NOT secure! Use bcrypt or passlib in production
    return hashed_password == f"hashed_{plain_password}"


def create_access_token(user_id: UUID) -> str:
    """Create a JWT access token.
    
    TODO: Implement proper JWT token generation.
    For now, this is a placeholder.
    """
    # SECURITY WARNING: This is NOT secure! Use python-jose or similar in production
    return f"token_{user_id}"


# -------------------- Routes -------------------- #

@router.post(
    "/register",
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """Register a new user (Admin or Player)."""
    try:
        # Hash the password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = repo_create_user(
            db=db,
            email=user_data.email,
            password_hash=password_hash,
            user_type=user_data.user_type,
            username=user_data.username,
        )
        
        return UserBase.model_validate(user)
    
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}",
        )


@router.post(
    "/login",
    response_model=UserLoginResponse,
    responses={401: {"model": ErrorResponse}},
)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """Login a user and return access token."""
    try:
        # Get user by email
        user = get_user_by_email(db, login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        # Create access token
        access_token = create_access_token(user.id)
        
        return UserLoginResponse(
            user=UserBase.model_validate(user),
            access_token=access_token,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login: {str(e)}",
        )


@router.get(
    "/",
    response_model=UserListResponse,
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all users."""
    try:
        users = get_all_users(db, skip=skip, limit=limit)
        return UserListResponse(
            users=[UserBase.model_validate(u) for u in users],
            total=len(users),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}",
        )


@router.get(
    "/{user_id}",
    response_model=UserBase,
    responses={404: {"model": ErrorResponse}},
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a user by ID."""
    try:
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return UserBase.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}",
        )


@router.get(
    "/players/list",
    response_model=List[PlayerUserResponse],
)
def list_players(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all player users."""
    try:
        players = get_all_players(db, skip=skip, limit=limit)
        return [PlayerUserResponse.model_validate(p) for p in players]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list players: {str(e)}",
        )


@router.post(
    "/players/assign-group",
    response_model=PlayerUserResponse,
    responses={404: {"model": ErrorResponse}},
)
def assign_player_to_group(
    assignment: PlayerAssignGroup,
    db: Session = Depends(get_db),
):
    """Assign a player to a group."""
    try:
        player = update_player_group(db, assignment.player_id, assignment.group_id)
        return PlayerUserResponse.model_validate(player)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign player to group: {str(e)}",
        )

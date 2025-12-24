# app/users/repository.py

from __future__ import annotations

from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import User, AdminUser, PlayerUser
from app.models.enums import UserType


class UserNotFoundError(Exception):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(Exception):
    """Raised when trying to create a user that already exists."""
    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""
    pass


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by their email."""
    return db.query(User).filter(User.email == email).first()


def get_admin_user(db: Session, user_id: UUID) -> Optional[AdminUser]:
    """Get an admin user by ID."""
    return db.query(AdminUser).filter(AdminUser.id == user_id).first()


def get_player_user(db: Session, user_id: UUID) -> Optional[PlayerUser]:
    """Get a player user by ID."""
    return db.query(PlayerUser).filter(PlayerUser.id == user_id).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def get_all_players(db: Session, skip: int = 0, limit: int = 100) -> list[PlayerUser]:
    """Get all player users with pagination."""
    return db.query(PlayerUser).offset(skip).limit(limit).all()


def create_user(
    db: Session,
    email: str,
    password_hash: str,
    user_type: UserType,
    username: Optional[str] = None,
    group_id: Optional[UUID] = None,
) -> User:
    """Create a new user (Admin or Player based on user_type).
    
    Note: This function expects password_hash, not plain password.
    Password hashing should be done before calling this function.
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise UserAlreadyExistsError(f"User with email {email} already exists")
    
    # Create appropriate user type
    if user_type == UserType.ADMIN:
        user = AdminUser(
            email=email,
            password_hash=password_hash,
            username=username,
            user_type=user_type,
        )
    elif user_type == UserType.PLAYER:
        user = PlayerUser(
            email=email,
            password_hash=password_hash,
            username=username,
            user_type=user_type,
            group_id=group_id,
        )
    else:
        raise ValueError(f"Invalid user type: {user_type}")
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_player_group(db: Session, player_id: UUID, group_id: UUID) -> PlayerUser:
    """Assign a player to a group."""
    player = get_player_user(db, player_id)
    if not player:
        raise UserNotFoundError(f"Player with id {player_id} not found")
    
    player.group_id = group_id
    db.commit()
    db.refresh(player)
    return player


def update_player_payment(db: Session, player_id: UUID, payment_amount: float) -> PlayerUser:
    """Update a player's payment amount."""
    player = get_player_user(db, player_id)
    if not player:
        raise UserNotFoundError(f"Player with id {player_id} not found")
    
    player.payment_amount_ils = payment_amount
    db.commit()
    db.refresh(player)
    return player


def delete_user(db: Session, user_id: UUID) -> bool:
    """Delete a user by ID."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise UserNotFoundError(f"User with id {user_id} not found")
    
    db.delete(user)
    db.commit()
    return True

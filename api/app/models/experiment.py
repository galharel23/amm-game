# app/models/experiment.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .base import Base


class Experiment(Base):
    """Experiment definition and configuration"""
    
    __tablename__ = "experiments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False)
    admin_id = Column(PG_UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False, index=True)
    num_rounds = Column(Integer, nullable=False)
    num_training_rounds = Column(Integer, nullable=False)
    num_rounds_for_payment = Column(Integer, nullable=False)
    num_players = Column(Integer, nullable=False)
    num_groups = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    admin = relationship("AdminUser", back_populates="experiments")
    rounds = relationship("Round", back_populates="experiment", cascade="all, delete-orphan")
    groups = relationship("Group", back_populates="experiment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Experiment(id={self.id}, name={self.name})>"


class Group(Base):
    """Player groups within an experiment"""
    
    __tablename__ = "groups"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(PG_UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False, index=True)
    group_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    experiment = relationship("Experiment", back_populates="groups")
    players = relationship("PlayerUser", back_populates="group")
    experiment_rounds = relationship("ExperimentRound", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group(id={self.id}, experiment_id={self.experiment_id}, number={self.group_number})>"

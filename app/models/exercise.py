from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.workout_exercise import WorkoutExercise


class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="muscle_group",
    )


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="equipment",
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    muscle_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("muscle_groups.id"),
        nullable=True,
    )

    equipment_id: Mapped[int | None] = mapped_column(
        ForeignKey("equipment.id"),
        nullable=True,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    muscle_group: Mapped["MuscleGroup | None"] = relationship(
        back_populates="exercises",
    )

    equipment: Mapped["Equipment | None"] = relationship(
        back_populates="exercises",
    )

    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="exercise",
    )
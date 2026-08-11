from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.workout_program import WorkoutProgram
    from app.models.workout_exercise import WorkoutExercise
    from app.models.workout_session import WorkoutSession


class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    workout_program_id: Mapped[int] = mapped_column(
        ForeignKey("workout_programs.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    day_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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

    program: Mapped["WorkoutProgram"] = relationship(
        back_populates="days",
    )

    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout_day",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.exercise_order",
    )

    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="workout_day",
    )
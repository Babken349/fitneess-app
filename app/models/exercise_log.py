from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.workout_session import WorkoutSession
    from app.models.exercise import Exercise
    from app.models.set_log import SetLog


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    __table_args__ = (
        UniqueConstraint(
            "workout_session_id",
            "exercise_id",
            name="uq_exercise_log_session_exercise",
        ),
        UniqueConstraint(
            "workout_session_id",
            "exercise_order",
            name="uq_exercise_log_session_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    workout_session_id: Mapped[int] = mapped_column(
        ForeignKey("workout_sessions.id"),
        nullable=False,
    )

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"),
        nullable=False,
    )

    exercise_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    workout_session: Mapped["WorkoutSession"] = relationship(
        back_populates="exercise_logs",
    )

    exercise: Mapped["Exercise"] = relationship()

    set_logs: Mapped[list["SetLog"]] = relationship(
        back_populates="exercise_log",
        cascade="all, delete-orphan",
        order_by="SetLog.set_number",
    )
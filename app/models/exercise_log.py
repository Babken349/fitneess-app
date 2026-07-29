from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.workout_session import WorkoutSession
    from app.models.exercise import Exercise
    from app.models.set_log import SetLog


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workout_session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)

    exercise_order: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    workout_session: Mapped["WorkoutSession"] = relationship(back_populates="exercise_logs")
    exercise: Mapped["Exercise"] = relationship()
    set_logs: Mapped[list["SetLog"]] = relationship(
        back_populates="exercise_log",
        cascade="all, delete-orphan",
        order_by="SetLog.set_number",
    )
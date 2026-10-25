from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.workout_day import WorkoutDay
    from app.models.exercise_log import ExerciseLog


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
)
    workout_day_id: Mapped[int | None] = mapped_column(ForeignKey("workout_days.id"), nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    user: Mapped["User"] = relationship(back_populates="workout_sessions")
    workout_day: Mapped["WorkoutDay | None"] = relationship()
    exercise_logs: Mapped[list["ExerciseLog"]] = relationship(
        back_populates="workout_session",
        cascade="all, delete-orphan",
        order_by="ExerciseLog.exercise_order",
    )
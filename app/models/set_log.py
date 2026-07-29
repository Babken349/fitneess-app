from typing import TYPE_CHECKING

from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.exercise_log import ExerciseLog


class SetLog(Base):
    __tablename__ = "set_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exercise_log_id: Mapped[int] = mapped_column(ForeignKey("exercise_logs.id"), nullable=False)

    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_weight: Mapped[float] = mapped_column(Float, nullable=False)
    rpe: Mapped[float | None] = mapped_column(Float, nullable=True)

    exercise_log: Mapped["ExerciseLog"] = relationship(back_populates="set_logs")
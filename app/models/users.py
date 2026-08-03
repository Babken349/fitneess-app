from datetime import datetime
from email.policy import default
from logging import RootLogger
from tokenize import StringPrefix
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.workout_program import WorkoutProgram
    from app.models.workout_session import WorkoutSession
    from app.models.body_weight import BodyWeight
    from app.models.achievement import Achievement
    from app.models.user_supplements import UserSupplement


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False, default="user")

    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    premium_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    workout_programs: Mapped[list["WorkoutProgram"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
    )
    body_weights: Mapped[list["BodyWeight"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
    )
    achievements: Mapped[list["Achievement"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    supplements: Mapped[list["UserSupplement"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
)
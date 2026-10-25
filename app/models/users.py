from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.body_measurement import BodyMeasurement
    from app.models.body_weight import BodyWeight
    from app.models.calendar_availability import CalendarAvailability
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.payment import Payment
    from app.models.progress_photo import ProgressPhoto
    from app.models.refresh_token import RefreshToken
    from app.models.reminder import Reminder
    from app.models.sleep import SleepEntry
    from app.models.study_state import StudyState
    from app.models.study_test_result import StudyTestResult
    from app.models.supplement_intake import SupplementIntake
    from app.models.user_achievement import UserAchievement
    from app.models.user_supplements import UserSupplement
    from app.models.workout_program import WorkoutProgram
    from app.models.workout_session import WorkoutSession
    from app.models.password_reset_token import PasswordResetToken


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

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    premium_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workout_programs: Mapped[list["WorkoutProgram"]] = relationship(
        "WorkoutProgram",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(
        "WorkoutSession",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    body_weights: Mapped[list["BodyWeight"]] = relationship(
        "BodyWeight",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    supplements: Mapped[list["UserSupplement"]] = relationship(
        "UserSupplement",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    body_measurements: Mapped[list["BodyMeasurement"]] = relationship(
        "BodyMeasurement",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="BodyMeasurement.recorded_at",
        passive_deletes=True,
    )

    progress_photos: Mapped[list["ProgressPhoto"]] = relationship(
        "ProgressPhoto",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ProgressPhoto.recorded_at",
        passive_deletes=True,
    )

    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    calendar_availability: Mapped[list["CalendarAvailability"]] = relationship(
        "CalendarAvailability",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    study_states: Mapped[list["StudyState"]] = relationship(
        "StudyState",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    sleep_records: Mapped[list["SleepEntry"]] = relationship(
        "SleepEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    study_test_results: Mapped[list["StudyTestResult"]] = relationship(
        "StudyTestResult",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    supplement_intakes: Mapped[list["SupplementIntake"]] = relationship(
        "SupplementIntake",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
"""Add email_verification_token and password_reset_token

Revision ID: 9fab6a5d83a2
Revises: dd8703617dd5
Create Date: 2026-08-26 19:41:09.071794

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9fab6a5d83a2"
down_revision: Union[str, Sequence[str], None] = "dd8703617dd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =========================================================
    # EMAIL VERIFICATION TOKENS
    # =========================================================

    # Старые записи уже существуют,
    # поэтому сначала добавляем token как nullable.
    op.add_column(
        "email_verification_tokens",
        sa.Column(
            "token",
            sa.String(length=255),
            nullable=True,
        ),
    )

    # Заполняем token для старых записей.
    # Эти значения нужны только для миграции старых данных.
    op.execute(
        """
        UPDATE email_verification_tokens
        SET token = 'legacy-token-' || id
        WHERE token IS NULL
        """
    )

    # Теперь можно сделать поле NOT NULL.
    op.alter_column(
        "email_verification_tokens",
        "token",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    # Удаляем старые индексы.
    op.drop_index(
        op.f("ix_email_verification_tokens_user_id"),
        table_name="email_verification_tokens",
    )

    op.drop_index(
        op.f("ix_email_verification_tokens_verification_token"),
        table_name="email_verification_tokens",
    )

    # Новый уникальный индекс token.
    op.create_index(
        op.f("ix_email_verification_tokens_token"),
        "email_verification_tokens",
        ["token"],
        unique=True,
    )

    # Пересоздаём FK.
    op.drop_constraint(
        op.f("email_verification_tokens_user_id_fkey"),
        "email_verification_tokens",
        type_="foreignkey",
    )

    op.create_foreign_key(
        None,
        "email_verification_tokens",
        "users",
        ["user_id"],
        ["id"],
    )

    # Старый verification_token больше не нужен.
    op.drop_column(
        "email_verification_tokens",
        "verification_token",
    )


    # =========================================================
    # REMINDERS
    # =========================================================

    # Здесь тоже могла существовать старая запись
    # с NULL user_supplement_id.
    #
    # Перед NOT NULL нужно убедиться, что таких записей нет.
    #
    # Если старые reminders действительно должны быть привязаны
    # к UserSupplement, их нужно заполнить вручную.
    #
    # Для миграции предполагаем, что NULL-записей нет.
    op.alter_column(
        "reminders",
        "user_supplement_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )


    # =========================================================
    # SUPPLEMENTS
    # =========================================================

    # Существующие записи получают NOW().
    op.add_column(
        "supplements",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "supplements",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.alter_column(
        "supplements",
        "description",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.String(length=500),
        existing_nullable=True,
    )

    op.create_index(
        op.f("ix_supplements_name"),
        "supplements",
        ["name"],
        unique=True,
    )


    # =========================================================
    # USER SUPPLEMENTS
    # =========================================================

    # ВАЖНО:
    # Старые записи существуют, поэтому нельзя сразу
    # добавить nullable=False без значения для старых строк.

    op.add_column(
        "user_supplements",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )

    # После добавления старые записи автоматически получают True.

    # Старые поля больше не нужны.
    op.drop_column(
        "user_supplements",
        "reminder_enabled",
    )

    op.drop_column(
        "user_supplements",
        "reminder_time",
    )

    op.drop_column(
        "user_supplements",
        "reminder_days",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # =========================================================
    # USER SUPPLEMENTS
    # =========================================================

    op.add_column(
        "user_supplements",
        sa.Column(
            "reminder_days",
            sa.VARCHAR(length=20),
            autoincrement=False,
            nullable=True,
        ),
    )

    op.add_column(
        "user_supplements",
        sa.Column(
            "reminder_time",
            postgresql.TIME(),
            autoincrement=False,
            nullable=True,
        ),
    )

    op.add_column(
        "user_supplements",
        sa.Column(
            "reminder_enabled",
            sa.BOOLEAN(),
            server_default=sa.true(),
            autoincrement=False,
            nullable=False,
        ),
    )

    op.drop_column(
        "user_supplements",
        "is_active",
    )


    # =========================================================
    # SUPPLEMENTS
    # =========================================================

    op.drop_index(
        op.f("ix_supplements_name"),
        table_name="supplements",
    )

    op.alter_column(
        "supplements",
        "description",
        existing_type=sa.String(length=500),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )

    op.drop_column(
        "supplements",
        "updated_at",
    )

    op.drop_column(
        "supplements",
        "created_at",
    )


    # =========================================================
    # REMINDERS
    # =========================================================

    op.alter_column(
        "reminders",
        "user_supplement_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )


    # =========================================================
    # EMAIL VERIFICATION TOKENS
    # =========================================================

    op.add_column(
        "email_verification_tokens",
        sa.Column(
            "verification_token",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=True,
        ),
    )

    # Восстанавливаем старые значения из token.
    op.execute(
        """
        UPDATE email_verification_tokens
        SET verification_token = token
        WHERE verification_token IS NULL
        """
    )

    op.alter_column(
        "email_verification_tokens",
        "verification_token",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
    )

    op.drop_constraint(
        None,
        "email_verification_tokens",
        type_="foreignkey",
    )

    op.create_foreign_key(
        op.f("email_verification_tokens_user_id_fkey"),
        "email_verification_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_index(
        op.f("ix_email_verification_tokens_token"),
        table_name="email_verification_tokens",
    )

    op.create_index(
        op.f("ix_email_verification_tokens_verification_token"),
        "email_verification_tokens",
        ["verification_token"],
        unique=True,
    )

    op.create_index(
        op.f("ix_email_verification_tokens_user_id"),
        "email_verification_tokens",
        ["user_id"],
        unique=False,
    )

    op.drop_column(
        "email_verification_tokens",
        "token",
    )
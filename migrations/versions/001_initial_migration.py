"""Начальная миграция с тестовыми данными

Revision ID: 001
Revises:
Create Date: 2024-01-01 12:00:00.000000

"""

from decimal import Decimal

import bcrypt
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table, column

# Идентификаторы ревизии, используемые Alembic
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def upgrade() -> None:
    # Создание таблиц
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admins_email"), "admins", ["email"], unique=True)
    op.create_index(op.f("ix_admins_id"), "admins", ["id"], unique=False)

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("balance", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_accounts_id"), "accounts", ["id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id", name="unique_transaction"),
    )
    op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)
    op.create_index(
        op.f("ix_payments_transaction_id"), "payments", ["transaction_id"], unique=False
    )

    # Вставка тестовых данных

    # Тестовый пользователь
    users_table = table(
        "users",
        column("id", sa.Integer),
        column("email", sa.String),
        column("full_name", sa.String),
        column("password_hash", sa.String),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Test User",
                "password_hash": hash_password("userpassword"),
            }
        ],
    )

    # Тестовый администратор
    admins_table = table(
        "admins",
        column("id", sa.Integer),
        column("email", sa.String),
        column("full_name", sa.String),
        column("password_hash", sa.String),
    )

    op.bulk_insert(
        admins_table,
        [
            {
                "id": 1,
                "email": "admin@example.com",
                "full_name": "Test Admin",
                "password_hash": hash_password("adminpassword"),
            }
        ],
    )

    # Тестовый счет
    accounts_table = table(
        "accounts",
        column("id", sa.Integer),
        column("user_id", sa.Integer),
        column("balance", sa.Numeric),
    )

    op.bulk_insert(
        accounts_table, [{"id": 1, "user_id": 1, "balance": Decimal("0.00")}]
    )


def downgrade() -> None:
    """Откат миграции - удаление всех созданных таблиц"""
    op.drop_index(op.f("ix_payments_transaction_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_accounts_id"), table_name="accounts")
    op.drop_table("accounts")
    op.drop_index(op.f("ix_admins_id"), table_name="admins")
    op.drop_index(op.f("ix_admins_email"), table_name="admins")
    op.drop_table("admins")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

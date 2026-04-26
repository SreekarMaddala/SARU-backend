"""Add split email/mobile and uniqueness guards

Revision ID: c9d7e4a1b2f3
Revises: a1b2c3d4e5f6
Create Date: 2026-04-26 12:15:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = "c9d7e4a1b2f3"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    users_cols = {c["name"] for c in insp.get_columns("users")}
    feedback_cols = {c["name"] for c in insp.get_columns("feedback")}

    # ---- users: split email/mobile and enforce uniqueness ----
    if "email" not in users_cols:
        op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    if "mobile" not in users_cols:
        op.add_column("users", sa.Column("mobile", sa.String(length=50), nullable=True))

    if "email_or_mobile" in users_cols:
        op.execute(text("""
            UPDATE users
            SET
              email = CASE
                WHEN email IS NULL AND email_or_mobile LIKE '%@%' THEN LOWER(BTRIM(email_or_mobile))
                ELSE email
              END,
              mobile = CASE
                WHEN mobile IS NULL AND email_or_mobile IS NOT NULL AND email_or_mobile NOT LIKE '%@%' THEN BTRIM(email_or_mobile)
                ELSE mobile
              END
        """))

    op.execute(text("""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'users_email_or_mobile_present_chk'
              AND conrelid = 'users'::regclass
          ) THEN
            ALTER TABLE users
              ADD CONSTRAINT users_email_or_mobile_present_chk
              CHECK (email IS NOT NULL OR mobile IS NOT NULL);
          END IF;
        END $$;
    """))

    op.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email_not_null
          ON users (email) WHERE email IS NOT NULL;
    """))
    op.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_mobile_not_null
          ON users (mobile) WHERE mobile IS NOT NULL;
    """))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_users_mobile ON users (mobile)"))

    # ---- feedback: split email/mobile and keep columns indexed ----
    if "email" not in feedback_cols:
        op.add_column("feedback", sa.Column("email", sa.String(length=255), nullable=True))
    if "mobile" not in feedback_cols:
        op.add_column("feedback", sa.Column("mobile", sa.String(length=50), nullable=True))

    if "email_or_mobile" in feedback_cols:
        op.execute(text("""
            UPDATE feedback
            SET
              email = CASE
                WHEN email IS NULL AND email_or_mobile LIKE '%@%' THEN LOWER(BTRIM(email_or_mobile))
                ELSE email
              END,
              mobile = CASE
                WHEN mobile IS NULL AND email_or_mobile IS NOT NULL AND email_or_mobile NOT LIKE '%@%' THEN BTRIM(email_or_mobile)
                ELSE mobile
              END
        """))

    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_email ON feedback (email)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_mobile ON feedback (mobile)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_company_id ON feedback (company_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_created_at ON feedback (created_at)"))


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    users_cols = {c["name"] for c in insp.get_columns("users")}
    feedback_cols = {c["name"] for c in insp.get_columns("feedback")}

    op.execute(text("DROP INDEX IF EXISTS ix_feedback_created_at"))
    op.execute(text("DROP INDEX IF EXISTS ix_feedback_mobile"))
    op.execute(text("DROP INDEX IF EXISTS ix_feedback_email"))

    if "email_or_mobile" not in feedback_cols:
        op.add_column("feedback", sa.Column("email_or_mobile", sa.String(length=100), nullable=True))

    if "email_or_mobile" in {c["name"] for c in insp.get_columns("feedback")}:
        op.execute(text("""
            UPDATE feedback
            SET email_or_mobile = COALESCE(email, mobile)
            WHERE email_or_mobile IS NULL
        """))

    if "email" in feedback_cols:
        op.drop_column("feedback", "email")
    if "mobile" in feedback_cols:
        op.drop_column("feedback", "mobile")

    op.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_or_mobile_present_chk"))
    op.execute(text("DROP INDEX IF EXISTS ux_users_email_not_null"))
    op.execute(text("DROP INDEX IF EXISTS ux_users_mobile_not_null"))
    op.execute(text("DROP INDEX IF EXISTS ix_users_email"))
    op.execute(text("DROP INDEX IF EXISTS ix_users_mobile"))

    if "email_or_mobile" not in users_cols:
        op.add_column("users", sa.Column("email_or_mobile", sa.String(length=100), nullable=True))

    if "email_or_mobile" in {c["name"] for c in insp.get_columns("users")}:
        op.execute(text("""
            UPDATE users
            SET email_or_mobile = COALESCE(email, mobile)
            WHERE email_or_mobile IS NULL
        """))

    if "email" in users_cols:
        op.drop_column("users", "email")
    if "mobile" in users_cols:
        op.drop_column("users", "mobile")

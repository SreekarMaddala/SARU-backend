"""Feedback delete cascades to related users

Revision ID: e3a1f9b7c2d4
Revises: c9d7e4a1b2f3
Create Date: 2026-04-26 13:55:00.000000
"""

from alembic import op
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "e3a1f9b7c2d4"
down_revision = "c9d7e4a1b2f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure deleting a user will delete all their feedback rows.
    op.execute(text("ALTER TABLE feedback DROP CONSTRAINT IF EXISTS feedback_user_id_fkey"))
    op.execute(text("""
        ALTER TABLE feedback
        ADD CONSTRAINT feedback_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    """))

    # When one feedback row is deleted, remove that related user.
    # The FK above then cascades and removes any remaining feedback rows for that user.
    op.execute(text("""
        CREATE OR REPLACE FUNCTION delete_user_after_feedback_delete()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF OLD.user_id IS NOT NULL THEN
                DELETE FROM users WHERE id = OLD.user_id;
            END IF;
            RETURN OLD;
        END;
        $$;
    """))

    op.execute(text("DROP TRIGGER IF EXISTS trg_feedback_delete_user ON feedback"))
    op.execute(text("""
        CREATE TRIGGER trg_feedback_delete_user
        AFTER DELETE ON feedback
        FOR EACH ROW
        EXECUTE FUNCTION delete_user_after_feedback_delete()
    """))


def downgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS trg_feedback_delete_user ON feedback"))
    op.execute(text("DROP FUNCTION IF EXISTS delete_user_after_feedback_delete()"))

    op.execute(text("ALTER TABLE feedback DROP CONSTRAINT IF EXISTS feedback_user_id_fkey"))
    op.execute(text("""
        ALTER TABLE feedback
        ADD CONSTRAINT feedback_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id)
    """))

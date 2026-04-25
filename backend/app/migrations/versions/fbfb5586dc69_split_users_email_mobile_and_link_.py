"""Split users email/mobile and link feedback by user_id

Revision ID: fbfb5586dc69
Revises: fbb9abf812b5
Create Date: 2026-04-25 20:49:57.278314

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect


# revision identifiers, used by Alembic.
revision = 'fbfb5586dc69'
down_revision = 'fbb9abf812b5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    users_cols = {c["name"] for c in insp.get_columns("users")}
    feedback_cols = {c["name"] for c in insp.get_columns("feedback")}

    # ---- Users: add id/email/mobile ----
    if "id" not in users_cols:
        op.add_column("users", sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=True))
        op.execute(text("CREATE SEQUENCE IF NOT EXISTS users_id_seq OWNED BY users.id"))
        op.execute(text("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')"))
        op.execute(text("UPDATE users SET id = nextval('users_id_seq') WHERE id IS NULL"))
        op.alter_column("users", "id", nullable=False)

    if "email" not in users_cols:
        op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    if "mobile" not in users_cols:
        op.add_column("users", sa.Column("mobile", sa.String(length=50), nullable=True))

    # Backfill email/mobile from legacy key users.email_or_mobile (if present)
    if "email_or_mobile" in users_cols:
        op.execute(text("""
            UPDATE users
            SET
              email  = CASE WHEN email IS NULL AND email_or_mobile LIKE '%@%' THEN email_or_mobile ELSE email END,
              mobile = CASE WHEN mobile IS NULL AND email_or_mobile IS NOT NULL AND email_or_mobile NOT LIKE '%@%' THEN email_or_mobile ELSE mobile END
        """))

    # Ensure PK is users.id (drop and recreate)
    op.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey"))
    op.execute(text("ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id)"))

    # At least one identifier
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

    # Unique indexes (partial)
    op.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email_not_null
          ON users (email) WHERE email IS NOT NULL;
    """))
    op.execute(text("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_mobile_not_null
          ON users (mobile) WHERE mobile IS NOT NULL;
    """))

    # Performance indexes (may duplicate SQLAlchemy's ix_*, but harmless)
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_users_mobile ON users (mobile)"))

    # ---- Feedback: add user_id, keep product/company FKs, cascade on product ----
    if "user_id" not in feedback_cols:
        op.add_column("feedback", sa.Column("user_id", sa.BigInteger(), nullable=True))

    # Backfill feedback.user_id using existing feedback.user_email_or_mobile -> users.email_or_mobile
    if "email_or_mobile" in users_cols and "user_email_or_mobile" in feedback_cols:
        op.execute(text("""
            UPDATE feedback f
            SET user_id = u.id
            FROM users u
            WHERE f.user_id IS NULL
              AND f.user_email_or_mobile IS NOT NULL
              AND u.email_or_mobile = f.user_email_or_mobile
        """))

    # Add FK feedback.user_id -> users.id
    op.execute(text("""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'feedback_user_id_fkey'
          ) THEN
            ALTER TABLE feedback
              ADD CONSTRAINT feedback_user_id_fkey
              FOREIGN KEY (user_id) REFERENCES users(id);
          END IF;
        END $$;
    """))

    # Ensure feedback.product_id FK has ON DELETE CASCADE
    op.execute(text("""
        DO $$
        DECLARE fk_name text;
        BEGIN
          SELECT conname INTO fk_name
          FROM pg_constraint
          WHERE conrelid = 'feedback'::regclass
            AND contype = 'f'
            AND pg_get_constraintdef(oid) LIKE '%FOREIGN KEY (product_id)%';
          IF fk_name IS NOT NULL THEN
            EXECUTE format('ALTER TABLE feedback DROP CONSTRAINT %I', fk_name);
          END IF;
          ALTER TABLE feedback
            ADD CONSTRAINT feedback_product_id_fkey
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
        END $$;
    """))

    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_user_id ON feedback (user_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_product_id ON feedback (product_id)"))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_company_id ON feedback (company_id)"))

    # ---- Products: unique (company_id, model_number) ----
    op.execute(text("""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conname = 'uq_products_company_id_model_number'
              AND conrelid = 'products'::regclass
          ) THEN
            ALTER TABLE products
              ADD CONSTRAINT uq_products_company_id_model_number
              UNIQUE (company_id, model_number);
          END IF;
        END $$;
    """))

    # ---- Cleanup legacy linkage columns ----
    if "user_email_or_mobile" in feedback_cols:
        op.drop_constraint("feedback_user_email_or_mobile_fkey", "feedback", type_="foreignkey", if_exists=True)
        op.drop_column("feedback", "user_email_or_mobile")

    if "email_or_mobile" in users_cols:
        # Drop old index if present then column
        op.execute(text("DROP INDEX IF EXISTS ix_users_email_or_mobile"))
        op.execute(text("DROP INDEX IF EXISTS users_email_or_mobile_key"))
        op.drop_column("users", "email_or_mobile")


def downgrade() -> None:
    # Best-effort downgrade (not fully reversible without data loss),
    # but keeps Alembic happy if you ever need to roll back.
    bind = op.get_bind()
    insp = inspect(bind)

    users_cols = {c["name"] for c in insp.get_columns("users")}
    feedback_cols = {c["name"] for c in insp.get_columns("feedback")}

    if "email_or_mobile" not in users_cols:
        op.add_column("users", sa.Column("email_or_mobile", sa.String(length=100), nullable=True))
        op.execute(text("""
            UPDATE users
            SET email_or_mobile = COALESCE(email, mobile)
            WHERE email_or_mobile IS NULL
        """))

    if "user_email_or_mobile" not in feedback_cols:
        op.add_column("feedback", sa.Column("user_email_or_mobile", sa.String(length=100), nullable=True))
        if "user_id" in feedback_cols:
            op.execute(text("""
                UPDATE feedback f
                SET user_email_or_mobile = u.email_or_mobile
                FROM users u
                WHERE f.user_id = u.id
            """))

    op.execute(text("ALTER TABLE feedback DROP CONSTRAINT IF EXISTS feedback_user_id_fkey"))
    if "user_id" in feedback_cols:
        op.drop_column("feedback", "user_id")

    # Drop new constraints/indexes
    op.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_or_mobile_present_chk"))
    op.execute(text("DROP INDEX IF EXISTS ux_users_email_not_null"))
    op.execute(text("DROP INDEX IF EXISTS ux_users_mobile_not_null"))
    op.execute(text("DROP INDEX IF EXISTS ix_users_email"))
    op.execute(text("DROP INDEX IF EXISTS ix_users_mobile"))
    op.execute(text("DROP INDEX IF EXISTS ix_feedback_user_id"))

    # Restore PK (legacy) if desired
    op.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey"))
    op.execute(text("ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (email_or_mobile)"))

    # Remove new columns (may lose data)
    if "email" in users_cols:
        op.drop_column("users", "email")
    if "mobile" in users_cols:
        op.drop_column("users", "mobile")

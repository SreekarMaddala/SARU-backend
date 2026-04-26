"""Remove product id, add composite PK (company_id, model_number)

Revision ID: a1b2c3d4e5f6
Revises: fbfb5586dc69
Create Date: 2026-04-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'fbfb5586dc69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    products_cols = {c["name"]: c for c in insp.get_columns("products")}
    feedback_cols = {c["name"]: c for c in insp.get_columns("feedback")}

    # ---- Feedback: migrate product_id -> product_model_number ----
    if "product_model_number" not in feedback_cols:
        op.add_column("feedback", sa.Column("product_model_number", sa.String(length=100), nullable=True))

    # Backfill product_model_number from products via product_id
    if "product_id" in feedback_cols:
        op.execute(text("""
            UPDATE feedback f
            SET product_model_number = p.model_number
            FROM products p
            WHERE f.product_id = p.id
              AND f.product_model_number IS NULL;
        """))

        # Drop old FK constraint
        op.execute(text("""
            ALTER TABLE feedback
            DROP CONSTRAINT IF EXISTS feedback_product_id_fkey;
        """))

        # Drop old index
        op.execute(text("DROP INDEX IF EXISTS ix_feedback_product_id"))

        # Drop product_id column
        op.drop_column("feedback", "product_id")

    # ---- Products: ensure model_number and company_id are NOT NULL ----
    # Delete products without model_number (they can't be part of a composite PK)
    op.execute(text("""
        DELETE FROM products
        WHERE model_number IS NULL OR model_number = '';
    """))

    # Delete products without company_id
    op.execute(text("""
        DELETE FROM products
        WHERE company_id IS NULL;
    """))

    # Make model_number NOT NULL
    op.alter_column("products", "model_number", nullable=False)

    # Make company_id NOT NULL
    op.alter_column("products", "company_id", nullable=False)

    # ---- Products: drop id column and sequence ----
    if "id" in products_cols:
        # Drop dependent default/sequence if exists
        op.execute(text("DROP SEQUENCE IF EXISTS products_id_seq CASCADE"))
        op.drop_column("products", "id")

    # Drop old unique constraint (replaced by PK)
    op.execute(text("""
        ALTER TABLE products
        DROP CONSTRAINT IF EXISTS uq_products_company_id_model_number;
    """))

    # Create composite primary key
    op.execute(text("""
        ALTER TABLE products
        ADD CONSTRAINT pk_products_company_id_model_number
        PRIMARY KEY (company_id, model_number);
    """))

    # Create composite FK on feedback (company_id, product_model_number) -> products
    op.execute(text("""
        ALTER TABLE feedback
        DROP CONSTRAINT IF EXISTS fk_feedback_product;
    """))
    op.execute(text("""
        ALTER TABLE feedback
        ADD CONSTRAINT fk_feedback_product
        FOREIGN KEY (company_id, product_model_number)
        REFERENCES products(company_id, model_number)
        ON DELETE CASCADE;
    """))

    # Create index on product_model_number
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_product_model_number ON feedback (product_model_number)"))


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    products_cols = {c["name"]: c for c in insp.get_columns("products")}
    feedback_cols = {c["name"]: c for c in insp.get_columns("feedback")}

    # ---- Feedback: restore product_id ----
    if "product_id" not in feedback_cols:
        op.add_column("feedback", sa.Column("product_id", sa.Integer(), nullable=True))

    # Backfill product_id (best effort - requires products to have been recreated with id)
    # This is lossy because we don't have the old id values
    if "product_model_number" in feedback_cols:
        op.execute(text("""
            UPDATE feedback f
            SET product_id = p.id
            FROM products p
            WHERE f.product_model_number = p.model_number
              AND f.company_id = p.company_id;
        """))

    # Drop composite FK
    op.execute(text("ALTER TABLE feedback DROP CONSTRAINT IF EXISTS fk_feedback_product"))

    # Drop product_model_number column and index
    op.execute(text("DROP INDEX IF EXISTS ix_feedback_product_model_number"))
    if "product_model_number" in feedback_cols:
        op.drop_column("feedback", "product_model_number")

    # Recreate product_id FK (will fail if products don't have id)
    op.execute(text("""
        ALTER TABLE feedback
        ADD CONSTRAINT feedback_product_id_fkey
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
    """))
    op.execute(text("CREATE INDEX IF NOT EXISTS ix_feedback_product_id ON feedback (product_id)"))

    # ---- Products: restore id column ----
    if "id" not in products_cols:
        op.add_column("products", sa.Column("id", sa.Integer(), autoincrement=True, nullable=True))
        op.execute(text("CREATE SEQUENCE IF NOT EXISTS products_id_seq OWNED BY products.id"))
        op.execute(text("ALTER TABLE products ALTER COLUMN id SET DEFAULT nextval('products_id_seq')"))
        op.execute(text("UPDATE products SET id = nextval('products_id_seq') WHERE id IS NULL"))
        op.alter_column("products", "id", nullable=False)

    # Drop composite PK
    op.execute(text("""
        ALTER TABLE products
        DROP CONSTRAINT IF EXISTS pk_products_company_id_model_number;
    """))

    # Restore primary key on id
    op.execute(text("""
        ALTER TABLE products
        ADD CONSTRAINT products_pkey PRIMARY KEY (id);
    """))

    # Recreate unique constraint
    op.execute(text("""
        ALTER TABLE products
        ADD CONSTRAINT uq_products_company_id_model_number
        UNIQUE (company_id, model_number);
    """))

    # Make columns nullable again
    op.alter_column("products", "model_number", nullable=True)
    op.alter_column("products", "company_id", nullable=True)


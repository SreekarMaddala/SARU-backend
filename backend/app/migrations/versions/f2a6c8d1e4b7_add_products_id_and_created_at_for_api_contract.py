"""Add products id and created_at for API contract

Revision ID: f2a6c8d1e4b7
Revises: e3a1f9b7c2d4
Create Date: 2026-04-26 14:05:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = "f2a6c8d1e4b7"
down_revision = "e3a1f9b7c2d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    products_cols = {c["name"] for c in insp.get_columns("products")}

    if "id" not in products_cols:
        op.add_column("products", sa.Column("id", sa.BigInteger(), nullable=True))
        op.execute(text("CREATE SEQUENCE IF NOT EXISTS products_api_id_seq OWNED BY products.id"))
        op.execute(text("ALTER TABLE products ALTER COLUMN id SET DEFAULT nextval('products_api_id_seq')"))
        op.execute(text("UPDATE products SET id = nextval('products_api_id_seq') WHERE id IS NULL"))
        op.execute(text("ALTER TABLE products ALTER COLUMN id SET NOT NULL"))
        op.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ux_products_id ON products (id)"))

    if "created_at" not in products_cols:
        op.add_column(
            "products",
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        )
        op.execute(text("UPDATE products SET created_at = now() WHERE created_at IS NULL"))
        op.execute(text("ALTER TABLE products ALTER COLUMN created_at SET NOT NULL"))


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    products_cols = {c["name"] for c in insp.get_columns("products")}

    if "created_at" in products_cols:
        op.drop_column("products", "created_at")

    if "id" in products_cols:
        op.execute(text("DROP INDEX IF EXISTS ux_products_id"))
        op.drop_column("products", "id")
        op.execute(text("DROP SEQUENCE IF EXISTS products_api_id_seq"))

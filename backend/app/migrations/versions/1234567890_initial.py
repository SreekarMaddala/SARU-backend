"""Initial migration

Revision ID: 1234567890
Revises:
Create Date: 2023-10-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1234567890'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('company_id', sa.String(), nullable=True),
        sa.Column('channel', sa.String(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('sentiment', sa.String(), nullable=True),
        sa.Column('topics', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True)
    )
    
    # Create indexes
    op.create_index(op.f('ix_feedback_company_id'), 'feedback', ['company_id'], unique=False)
    op.create_index(op.f('ix_feedback_id'), 'feedback', ['id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_feedback_id'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_company_id'), table_name='feedback')
    
    # Drop table
    op.drop_table('feedback')

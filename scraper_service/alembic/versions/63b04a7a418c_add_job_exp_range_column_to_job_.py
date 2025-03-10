"""Add job_exp_range column to job_subscriptions table

Revision ID: 63b04a7a418c
Revises: 8d07eb57f3c6
Create Date: 2025-03-10 06:32:35.609033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63b04a7a418c'
down_revision: Union[str, None] = '8d07eb57f3c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('job_subscriptions', sa.Column('job_exp_range', sa.JSON(), nullable=False, server_default='{}'))



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('job_subscriptions', 'job_exp_range')


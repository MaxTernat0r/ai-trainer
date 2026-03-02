"""add_is_completed_to_scheduled_workouts

Revision ID: 1ac04756e3e7
Revises: e5b2a9d71f4c
Create Date: 2026-03-01 16:38:34.914053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ac04756e3e7'
down_revision: Union[str, None] = 'e5b2a9d71f4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('scheduled_workouts', sa.Column('is_completed', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    op.drop_column('scheduled_workouts', 'is_completed')

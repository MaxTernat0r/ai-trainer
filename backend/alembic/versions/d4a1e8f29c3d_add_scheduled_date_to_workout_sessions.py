"""add_scheduled_date_to_workout_sessions

Revision ID: d4a1e8f29c3d
Revises: c879e0b3b1c5
Create Date: 2026-03-01 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4a1e8f29c3d'
down_revision: Union[str, None] = 'c879e0b3b1c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('workout_sessions', sa.Column('scheduled_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('workout_sessions', 'scheduled_date')

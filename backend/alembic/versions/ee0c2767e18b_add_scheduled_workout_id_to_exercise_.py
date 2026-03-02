"""add_scheduled_workout_id_to_exercise_sets

Revision ID: ee0c2767e18b
Revises: 1ac04756e3e7
Create Date: 2026-03-01 16:53:04.318133

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee0c2767e18b'
down_revision: Union[str, None] = '1ac04756e3e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('exercise_sets', sa.Column('scheduled_workout_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_exercise_sets_scheduled_workout',
        'exercise_sets', 'scheduled_workouts',
        ['scheduled_workout_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_exercise_sets_scheduled_workout', 'exercise_sets', type_='foreignkey')
    op.drop_column('exercise_sets', 'scheduled_workout_id')

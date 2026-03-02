"""add_scheduled_workouts_table

Revision ID: e5b2a9d71f4c
Revises: d4a1e8f29c3d
Create Date: 2026-03-01 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e5b2a9d71f4c'
down_revision: Union[str, None] = 'd4a1e8f29c3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scheduled_workouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('workout_plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workout_plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workout_session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workout_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_scheduled_workouts_plan_date', 'scheduled_workouts', ['workout_plan_id', 'scheduled_date'])


def downgrade() -> None:
    op.drop_index('ix_scheduled_workouts_plan_date', table_name='scheduled_workouts')
    op.drop_table('scheduled_workouts')

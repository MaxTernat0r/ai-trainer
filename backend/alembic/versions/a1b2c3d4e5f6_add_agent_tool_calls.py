"""add_agent_tool_calls

Revision ID: a1b2c3d4e5f6
Revises: 7f2c1d8a9b3e
Create Date: 2026-05-24 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7f2c1d8a9b3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'agent_tool_calls',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('tool_name', sa.String(length=60), nullable=False),
        sa.Column('arguments', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_proposal', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pending_messages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['chat_conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_agent_tool_calls_user_created', 'agent_tool_calls', ['user_id', 'created_at'])
    op.create_index('ix_agent_tool_calls_conversation', 'agent_tool_calls', ['conversation_id'])


def downgrade() -> None:
    op.drop_index('ix_agent_tool_calls_conversation', table_name='agent_tool_calls')
    op.drop_index('ix_agent_tool_calls_user_created', table_name='agent_tool_calls')
    op.drop_table('agent_tool_calls')

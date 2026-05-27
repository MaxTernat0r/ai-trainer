"""Lowercase emails + unique index on lower(email)

Revision ID: f3a91d2c8e4b
Revises: a1b2c3d4e5f6
Create Date: 2026-05-26
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f3a91d2c8e4b"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # If a previous run left case-only collisions intact (e.g. "Foo@x.com"
    # plus "foo@x.com"), the unique-index step below would die mid-deploy.
    # Resolve them deterministically: keep the verified peer (or the older
    # one when both are unverified), rename the loser by appending its id
    # so the row survives in DB but no longer collides on lower(email).
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                email,
                row_number() OVER (
                    PARTITION BY lower(email)
                    ORDER BY is_verified DESC NULLS LAST, created_at ASC, id ASC
                ) AS rn
            FROM users
        )
        UPDATE users u
        SET email = u.email || '+collision-' || substr(u.id::text, 1, 8)
        FROM ranked r
        WHERE u.id = r.id
          AND r.rn > 1
          AND lower(u.email) IN (
              SELECT lower(email) FROM users
              GROUP BY lower(email) HAVING count(*) > 1
          )
        """
    )

    # Normalize the surviving rows to lowercase. After the dedup pass above
    # there are no remaining lower(email) collisions, so this is now safe.
    op.execute("UPDATE users SET email = lower(email) WHERE email <> lower(email)")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_lower "
        "ON users (lower(email))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_users_email_lower")

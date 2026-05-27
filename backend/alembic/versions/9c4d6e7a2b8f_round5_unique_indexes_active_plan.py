"""Round 5 hardening: unique constraints, FK indexes, one-active-plan-per-user

Revision ID: 9c4d6e7a2b8f
Revises: f3a91d2c8e4b
Create Date: 2026-05-27

Adds three groups of constraints in one shot:

1. Idempotency uniques — weight_logs, measurement_logs, exercise_sets,
   scheduled_workouts. Routers in round 5 already rely on IntegrityError
   here to do upsert-on-same-key. Without these indexes the upsert paths
   in routers/analytics.py and routers/workouts.py never fire and we end
   up with duplicate rows that make weight_change_30d / streak flicker.

2. FK indexes on hot join paths. Postgres does NOT auto-index FK columns,
   and most read paths join on user_id / plan_id / session_id. These show
   up as seq scans in pg_stat_statements once you have any volume.

3. Partial unique on (user_id) where is_active=True for both workout and
   nutrition plans. set_active_plan does mass UPDATE...is_active=False
   followed by single UPDATE...is_active=True; under concurrent calls
   (or a partially-rolled-back transaction) you can end up with two
   active plans per user, which the dashboard / chat agent then surfaces
   inconsistently. Partial unique makes the second concurrent setter
   fail loudly instead of silently corrupting state.

Each step is preceded by a dedup pass so the index creation does not
crash mid-deploy on existing duplicates.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "9c4d6e7a2b8f"
down_revision: Union[str, None] = "f3a91d2c8e4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------- 1. dedup before adding uniques ----------

    # weight_logs: one per (user, day). Keep oldest, delete rest.
    op.execute(
        """
        DELETE FROM weight_logs w
        USING (
            SELECT id, row_number() OVER (
                PARTITION BY user_id, logged_at
                ORDER BY created_at ASC, id ASC
            ) AS rn
            FROM weight_logs
        ) r
        WHERE w.id = r.id AND r.rn > 1
        """
    )

    # measurement_logs: one per (user, type, day).
    op.execute(
        """
        DELETE FROM measurement_logs m
        USING (
            SELECT id, row_number() OVER (
                PARTITION BY user_id, measurement_type, logged_at
                ORDER BY created_at ASC, id ASC
            ) AS rn
            FROM measurement_logs
        ) r
        WHERE m.id = r.id AND r.rn > 1
        """
    )

    # exercise_sets: one per (workout_exercise, scheduled_workout, set_number).
    # scheduled_workout_id is nullable; treat NULLs as distinct (default
    # NULLS DISTINCT works fine on PG <15 too — duplicate (we_id, NULL,
    # set_number) rows would simply not collide). We still want to dedup
    # rows that are exact duplicates including a real scheduled_workout_id.
    op.execute(
        """
        DELETE FROM exercise_sets s
        USING (
            SELECT id, row_number() OVER (
                PARTITION BY workout_exercise_id, scheduled_workout_id, set_number
                ORDER BY completed_at ASC, id ASC
            ) AS rn
            FROM exercise_sets
            WHERE scheduled_workout_id IS NOT NULL
        ) r
        WHERE s.id = r.id AND r.rn > 1
        """
    )

    # scheduled_workouts: one per (session, date).
    op.execute(
        """
        DELETE FROM scheduled_workouts sw
        USING (
            SELECT id, row_number() OVER (
                PARTITION BY workout_session_id, scheduled_date
                ORDER BY created_at ASC, id ASC
            ) AS rn
            FROM scheduled_workouts
        ) r
        WHERE sw.id = r.id AND r.rn > 1
        """
    )

    # food_items: dedup by lower(name_ru). Same approach as the email dedup
    # in f3a91d2c8e4b — keep the verified peer, then the oldest. Re-point
    # meal_items / nutrition_logs that pointed at a loser to the survivor
    # so we don't break referential integrity.
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                lower(name_ru) AS key,
                row_number() OVER (
                    PARTITION BY lower(name_ru)
                    ORDER BY is_verified DESC NULLS LAST, created_at ASC, id ASC
                ) AS rn
            FROM food_items
        ),
        survivors AS (
            SELECT key, id AS survivor_id FROM ranked WHERE rn = 1
        ),
        losers AS (
            SELECT r.id AS loser_id, s.survivor_id
            FROM ranked r
            JOIN survivors s ON s.key = r.key
            WHERE r.rn > 1
        )
        UPDATE meal_items mi
        SET food_item_id = l.survivor_id
        FROM losers l
        WHERE mi.food_item_id = l.loser_id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                lower(name_ru) AS key,
                row_number() OVER (
                    PARTITION BY lower(name_ru)
                    ORDER BY is_verified DESC NULLS LAST, created_at ASC, id ASC
                ) AS rn
            FROM food_items
        ),
        survivors AS (
            SELECT key, id AS survivor_id FROM ranked WHERE rn = 1
        ),
        losers AS (
            SELECT r.id AS loser_id, s.survivor_id
            FROM ranked r
            JOIN survivors s ON s.key = r.key
            WHERE r.rn > 1
        )
        UPDATE nutrition_logs nl
        SET food_item_id = l.survivor_id
        FROM losers l
        WHERE nl.food_item_id = l.loser_id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                row_number() OVER (
                    PARTITION BY lower(name_ru)
                    ORDER BY is_verified DESC NULLS LAST, created_at ASC, id ASC
                ) AS rn
            FROM food_items
        )
        DELETE FROM food_items f
        USING ranked r
        WHERE f.id = r.id AND r.rn > 1
        """
    )

    # active-plan dedup: keep the most recently updated active plan per user.
    op.execute(
        """
        WITH ranked AS (
            SELECT id, row_number() OVER (
                PARTITION BY user_id
                ORDER BY updated_at DESC NULLS LAST, created_at DESC, id DESC
            ) AS rn
            FROM workout_plans
            WHERE is_active = TRUE
        )
        UPDATE workout_plans p
        SET is_active = FALSE
        FROM ranked r
        WHERE p.id = r.id AND r.rn > 1
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT id, row_number() OVER (
                PARTITION BY user_id
                ORDER BY updated_at DESC NULLS LAST, created_at DESC, id DESC
            ) AS rn
            FROM nutrition_plans
            WHERE is_active = TRUE
        )
        UPDATE nutrition_plans p
        SET is_active = FALSE
        FROM ranked r
        WHERE p.id = r.id AND r.rn > 1
        """
    )

    # ---------- 2. unique indexes ----------
    #
    # Everything below uses CREATE [UNIQUE] INDEX IF NOT EXISTS via op.execute
    # because:
    #  - some hot-path indexes (ix_scheduled_workouts_plan_date,
    #    ix_weight_logs_user_date, ix_measurement_logs_user_type_date) already
    #    exist on prod from earlier migrations or hand-applied DDL, and
    #  - this migration runs in a single transaction, so a single duplicate
    #    would otherwise rollback the whole round-5 hardening.

    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_weight_logs_user_date "
        "ON weight_logs (user_id, logged_at)"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_measurement_logs_user_type_date "
        "ON measurement_logs (user_id, measurement_type, logged_at)"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_exercise_sets_we_sw_setnum "
        "ON exercise_sets (workout_exercise_id, scheduled_workout_id, set_number) "
        "WHERE scheduled_workout_id IS NOT NULL"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_scheduled_workouts_session_date "
        "ON scheduled_workouts (workout_session_id, scheduled_date)"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_food_items_name_ru_lower "
        "ON food_items (lower(name_ru))"
    )

    # ---------- 3. partial unique for one active plan per user ----------

    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_workout_plans_one_active_per_user "
        "ON workout_plans (user_id) WHERE is_active = TRUE"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_nutrition_plans_one_active_per_user "
        "ON nutrition_plans (user_id) WHERE is_active = TRUE"
    )

    # ---------- 4. FK / hot-path indexes ----------

    # Workouts vertical: every read joins down from user → plan → session →
    # exercise → set, plus calendar reads which filter by scheduled_date.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_workout_plans_user_id "
        "ON workout_plans (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_workout_plans_user_active "
        "ON workout_plans (user_id) WHERE is_active = TRUE"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_workout_sessions_plan_id "
        "ON workout_sessions (workout_plan_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_workout_exercises_session_id "
        "ON workout_exercises (workout_session_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_workout_exercises_exercise_id "
        "ON workout_exercises (exercise_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_exercise_sets_workout_exercise_id "
        "ON exercise_sets (workout_exercise_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_exercise_sets_scheduled_workout_id "
        "ON exercise_sets (scheduled_workout_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_scheduled_workouts_plan_id "
        "ON scheduled_workouts (workout_plan_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_scheduled_workouts_session_id "
        "ON scheduled_workouts (workout_session_id)"
    )
    # ix_scheduled_workouts_plan_date is created by e5b2a9d71f4c — we only
    # ensure it via IF NOT EXISTS in case of hand-applied DDL drift.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_scheduled_workouts_plan_date "
        "ON scheduled_workouts (workout_plan_id, scheduled_date)"
    )

    # Nutrition vertical.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_nutrition_plans_user_id "
        "ON nutrition_plans (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_nutrition_plans_user_active "
        "ON nutrition_plans (user_id) WHERE is_active = TRUE"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_meals_nutrition_plan_id "
        "ON meals (nutrition_plan_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_meal_items_meal_id ON meal_items (meal_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_meal_items_food_item_id "
        "ON meal_items (food_item_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_nutrition_logs_user_date "
        "ON nutrition_logs (user_id, logged_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_nutrition_logs_food_item_id "
        "ON nutrition_logs (food_item_id)"
    )

    # Chat / agent: hot path is "load last 20 messages of conversation".
    # The agent_tool_calls audit log already has two composite indexes from
    # the model __table_args__.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_conversations_user_id "
        "ON chat_conversations (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_chat_messages_conversation_created "
        "ON chat_messages (conversation_id, created_at)"
    )

    # Auth: refresh_token lookup by user_id.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_refresh_tokens_user_id "
        "ON refresh_tokens (user_id)"
    )

    # Analytics: weight_logs / measurement_logs already have composite
    # (user_id, ...) indexes from the model definition (ix_weight_logs_user_date,
    # ix_measurement_logs_user_type_date). The new uniques above ALSO support
    # index lookups on the same prefixes, so we don't recreate them here.


def downgrade() -> None:
    # Indexes (drop in reverse order of creation; IF EXISTS so re-runs are safe).
    op.execute("DROP INDEX IF EXISTS ix_refresh_tokens_user_id")
    op.execute("DROP INDEX IF EXISTS ix_chat_messages_conversation_created")
    op.execute("DROP INDEX IF EXISTS ix_chat_conversations_user_id")
    op.execute("DROP INDEX IF EXISTS ix_nutrition_logs_food_item_id")
    op.execute("DROP INDEX IF EXISTS ix_nutrition_logs_user_date")
    op.execute("DROP INDEX IF EXISTS ix_meal_items_food_item_id")
    op.execute("DROP INDEX IF EXISTS ix_meal_items_meal_id")
    op.execute("DROP INDEX IF EXISTS ix_meals_nutrition_plan_id")
    op.execute("DROP INDEX IF EXISTS ix_nutrition_plans_user_active")
    op.execute("DROP INDEX IF EXISTS ix_nutrition_plans_user_id")
    op.execute("DROP INDEX IF EXISTS ix_scheduled_workouts_plan_date")
    op.execute("DROP INDEX IF EXISTS ix_scheduled_workouts_session_id")
    op.execute("DROP INDEX IF EXISTS ix_scheduled_workouts_plan_id")
    op.execute("DROP INDEX IF EXISTS ix_exercise_sets_scheduled_workout_id")
    op.execute("DROP INDEX IF EXISTS ix_exercise_sets_workout_exercise_id")
    op.execute("DROP INDEX IF EXISTS ix_workout_exercises_exercise_id")
    op.execute("DROP INDEX IF EXISTS ix_workout_exercises_session_id")
    op.execute("DROP INDEX IF EXISTS ix_workout_sessions_plan_id")
    op.execute("DROP INDEX IF EXISTS ix_workout_plans_user_active")
    op.execute("DROP INDEX IF EXISTS ix_workout_plans_user_id")

    op.execute("DROP INDEX IF EXISTS uq_nutrition_plans_one_active_per_user")
    op.execute("DROP INDEX IF EXISTS uq_workout_plans_one_active_per_user")
    op.execute("DROP INDEX IF EXISTS uq_food_items_name_ru_lower")
    op.execute("DROP INDEX IF EXISTS uq_scheduled_workouts_session_date")
    op.execute("DROP INDEX IF EXISTS uq_exercise_sets_we_sw_setnum")
    op.execute("DROP INDEX IF EXISTS uq_measurement_logs_user_type_date")
    op.execute("DROP INDEX IF EXISTS uq_weight_logs_user_date")

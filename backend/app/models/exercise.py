import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_model import BaseModel


class MuscleGroup(BaseModel):
    __tablename__ = "muscle_groups"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    body_area: Mapped[str] = mapped_column(String(50), nullable=False)


class Equipment(BaseModel):
    __tablename__ = "equipment"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)


class Exercise(BaseModel):
    __tablename__ = "exercises"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    exercise_type: Mapped[str] = mapped_column(String(30), nullable=False)
    equipment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=True
    )
    model_3d_key: Mapped[str | None] = mapped_column(String(100), nullable=True)

    equipment: Mapped["Equipment | None"] = relationship(lazy="selectin")
    muscle_groups: Mapped[list["ExerciseMuscleGroup"]] = relationship(
        back_populates="exercise", lazy="selectin"
    )


class ExerciseMuscleGroup(BaseModel):
    __tablename__ = "exercise_muscle_groups"

    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    muscle_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("muscle_groups.id", ondelete="CASCADE"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)

    exercise: Mapped["Exercise"] = relationship(back_populates="muscle_groups")
    muscle_group: Mapped["MuscleGroup"] = relationship(lazy="selectin")

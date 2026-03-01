from pydantic import BaseModel


class MuscleGroupRead(BaseModel):
    id: str
    name: str
    name_ru: str
    body_area: str

    model_config = {"from_attributes": True}


class EquipmentRead(BaseModel):
    id: str
    name: str
    name_ru: str
    category: str

    model_config = {"from_attributes": True}


class ExerciseMuscleGroupRead(BaseModel):
    muscle_group: MuscleGroupRead
    is_primary: bool

    model_config = {"from_attributes": True}


class ExerciseRead(BaseModel):
    id: str
    name: str
    name_ru: str
    description: str | None = None
    description_ru: str | None = None
    instructions: str | None = None
    instructions_ru: str | None = None
    difficulty: str
    exercise_type: str
    equipment: EquipmentRead | None = None
    model_3d_key: str | None = None
    muscle_groups: list[ExerciseMuscleGroupRead] = []

    model_config = {"from_attributes": True}


class ExerciseListRead(BaseModel):
    id: str
    name: str
    name_ru: str
    difficulty: str
    exercise_type: str
    equipment: EquipmentRead | None = None
    model_3d_key: str | None = None

    model_config = {"from_attributes": True}

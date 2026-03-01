"""Seed data for exercises.

Contains 85 exercises covering all major muscle groups with full Russian translations,
step-by-step instructions, difficulty levels, and muscle group mappings.
"""

EXERCISES = [
    # ========================================================================
    # CHEST (Грудь)
    # ========================================================================
    {
        "name": "Barbell Bench Press",
        "name_ru": "Жим штанги лёжа",
        "description_ru": "Базовое упражнение для развития грудных мышц, передних дельт и трицепсов.",
        "instructions_ru": (
            "1. Лягте на горизонтальную скамью, стопы плотно на полу.\n"
            "2. Возьмите штангу хватом чуть шире плеч.\n"
            "3. Снимите штангу со стоек и зафиксируйте над грудью.\n"
            "4. На вдохе плавно опустите штангу к середине груди.\n"
            "5. На выдохе выжмите штангу вверх до полного выпрямления рук.\n"
            "6. Не отрывайте поясницу от скамьи, сохраняйте естественный прогиб."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },
    {
        "name": "Incline Barbell Bench Press",
        "name_ru": "Жим штанги на наклонной скамье",
        "description_ru": "Упражнение для развития верхней части грудных мышц.",
        "instructions_ru": (
            "1. Установите скамью под углом 30–45 градусов.\n"
            "2. Лягте на скамью, стопы плотно на полу.\n"
            "3. Возьмите штангу хватом чуть шире плеч.\n"
            "4. На вдохе опустите штангу к верхней части груди.\n"
            "5. На выдохе выжмите штангу вверх.\n"
            "6. Контролируйте движение, не используйте инерцию."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },
    {
        "name": "Decline Barbell Bench Press",
        "name_ru": "Жим штанги на скамье с отрицательным наклоном",
        "description_ru": "Упражнение для акцентированной проработки нижней части грудных мышц.",
        "instructions_ru": (
            "1. Установите скамью под отрицательным углом 15–30 градусов.\n"
            "2. Закрепите ноги за валики, лягте на скамью.\n"
            "3. Возьмите штангу хватом чуть шире плеч.\n"
            "4. На вдохе опустите штангу к нижней части груди.\n"
            "5. На выдохе выжмите штангу вверх до полного выпрямления рук.\n"
            "6. Работайте с напарником для безопасности."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },
    {
        "name": "Dumbbell Bench Press",
        "name_ru": "Жим гантелей лёжа",
        "description_ru": "Упражнение для грудных мышц с увеличенной амплитудой движения.",
        "instructions_ru": (
            "1. Лягте на горизонтальную скамью с гантелями в руках.\n"
            "2. Выжмите гантели вверх, ладони направлены вперёд.\n"
            "3. На вдохе разведите гантели в стороны, опуская к уровню груди.\n"
            "4. На выдохе выжмите гантели вверх, сводя их друг к другу.\n"
            "5. В верхней точке не ударяйте гантели друг о друга."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },
    {
        "name": "Incline Dumbbell Press",
        "name_ru": "Жим гантелей на наклонной скамье",
        "description_ru": "Упражнение для верхней части грудных мышц с гантелями.",
        "instructions_ru": (
            "1. Установите скамью под углом 30–45 градусов.\n"
            "2. Сядьте на скамью, поднимите гантели к плечам.\n"
            "3. На выдохе выжмите гантели вверх.\n"
            "4. На вдохе медленно опустите гантели до уровня груди.\n"
            "5. Сохраняйте контроль на протяжении всего движения."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },
    {
        "name": "Push-Up",
        "name_ru": "Отжимания от пола",
        "description_ru": "Базовое упражнение с собственным весом для груди, плеч и трицепсов.",
        "instructions_ru": (
            "1. Примите упор лёжа, руки чуть шире плеч.\n"
            "2. Тело должно образовывать прямую линию от головы до пят.\n"
            "3. На вдохе согните руки и опуститесь, пока грудь почти не коснётся пола.\n"
            "4. На выдохе отожмитесь вверх до полного выпрямления рук.\n"
            "5. Не прогибайте поясницу и не поднимайте таз."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": None,
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps", "rectus_abdominis"],
    },
    {
        "name": "Cable Crossover",
        "name_ru": "Сведение рук в кроссовере",
        "description_ru": "Изолирующее упражнение для грудных мышц на блочном тренажёре.",
        "instructions_ru": (
            "1. Установите блоки на верхний уровень.\n"
            "2. Встаньте между стойками, возьмитесь за рукоятки.\n"
            "3. Сделайте небольшой шаг вперёд, слегка наклоните корпус.\n"
            "4. На выдохе сведите руки перед собой дугообразным движением.\n"
            "5. На вдохе медленно разведите руки в стороны.\n"
            "6. Сохраняйте небольшой сгиб в локтях на протяжении движения."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "cable_machine",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior"],
    },
    {
        "name": "Pec Deck Fly",
        "name_ru": "Сведение рук в тренажёре бабочка",
        "description_ru": "Изолирующее упражнение для грудных мышц в тренажёре.",
        "instructions_ru": (
            "1. Сядьте в тренажёр, прижмите спину к спинке.\n"
            "2. Возьмитесь за рукоятки, локти слегка согнуты.\n"
            "3. На выдохе сведите руки перед собой.\n"
            "4. Задержитесь на секунду в точке максимального сокращения.\n"
            "5. На вдохе медленно вернитесь в исходное положение."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "pec_deck",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior"],
    },
    {
        "name": "Chest Dips",
        "name_ru": "Отжимания на брусьях (грудной вариант)",
        "description_ru": "Упражнение на брусьях с акцентом на нижнюю часть грудных мышц.",
        "instructions_ru": (
            "1. Примите упор на брусьях, руки выпрямлены.\n"
            "2. Наклоните корпус вперёд примерно на 30 градусов.\n"
            "3. На вдохе медленно опуститесь, разводя локти в стороны.\n"
            "4. Опускайтесь до комфортного растяжения грудных мышц.\n"
            "5. На выдохе отожмитесь вверх до выпрямления рук.\n"
            "6. Сохраняйте наклон корпуса на протяжении всего подхода."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "parallel_bars",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },

    # ========================================================================
    # BACK (Спина)
    # ========================================================================
    {
        "name": "Pull-Up",
        "name_ru": "Подтягивания",
        "description_ru": "Базовое упражнение с собственным весом для развития широчайших мышц спины.",
        "instructions_ru": (
            "1. Повисните на турнике хватом чуть шире плеч, ладони от себя.\n"
            "2. На выдохе подтянитесь, стремясь дотянуться подбородком до перекладины.\n"
            "3. Сведите лопатки в верхней точке.\n"
            "4. На вдохе медленно опуститесь в исходное положение.\n"
            "5. Не раскачивайтесь и не используйте инерцию."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "pull_up_bar",
        "primary_muscles": ["latissimus_dorsi"],
        "secondary_muscles": ["biceps", "rhomboids", "trapezius"],
    },
    {
        "name": "Lat Pulldown",
        "name_ru": "Тяга верхнего блока к груди",
        "description_ru": "Упражнение на блочном тренажёре для широчайших мышц спины.",
        "instructions_ru": (
            "1. Сядьте за тренажёр, зафиксируйте бёдра под валиками.\n"
            "2. Возьмите рукоять широким хватом.\n"
            "3. На выдохе потяните рукоять к верхней части груди.\n"
            "4. Сведите лопатки, слегка отклонив корпус назад.\n"
            "5. На вдохе медленно вернитесь в исходное положение.\n"
            "6. Не тяните рукоять за голову — это травмоопасно."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "lat_pulldown",
        "primary_muscles": ["latissimus_dorsi"],
        "secondary_muscles": ["biceps", "rhomboids"],
    },
    {
        "name": "Barbell Bent-Over Row",
        "name_ru": "Тяга штанги в наклоне",
        "description_ru": "Базовое упражнение для толщины и ширины спины.",
        "instructions_ru": (
            "1. Возьмите штангу хватом на ширине плеч.\n"
            "2. Наклонитесь вперёд до угла 45 градусов, спина прямая.\n"
            "3. Колени слегка согнуты, штанга висит на вытянутых руках.\n"
            "4. На выдохе подтяните штангу к низу живота.\n"
            "5. Сведите лопатки в верхней точке.\n"
            "6. На вдохе медленно опустите штангу."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["latissimus_dorsi", "rhomboids"],
        "secondary_muscles": ["biceps", "erector_spinae", "trapezius"],
    },
    {
        "name": "Dumbbell One-Arm Row",
        "name_ru": "Тяга гантели в наклоне одной рукой",
        "description_ru": "Упражнение для спины с акцентом на одностороннюю проработку.",
        "instructions_ru": (
            "1. Поставьте одно колено и руку на скамью для опоры.\n"
            "2. Возьмите гантель в свободную руку.\n"
            "3. Спина параллельна полу, взгляд вниз.\n"
            "4. На выдохе подтяните гантель к поясу, отводя локоть назад.\n"
            "5. Сведите лопатку в верхней точке.\n"
            "6. На вдохе плавно опустите гантель."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["latissimus_dorsi"],
        "secondary_muscles": ["biceps", "rhomboids", "trapezius"],
    },
    {
        "name": "Seated Cable Row",
        "name_ru": "Тяга нижнего блока к поясу",
        "description_ru": "Упражнение для средней части спины на блочном тренажёре.",
        "instructions_ru": (
            "1. Сядьте за тренажёр, упритесь стопами в платформу.\n"
            "2. Возьмитесь за V-образную рукоять.\n"
            "3. Спина прямая, колени слегка согнуты.\n"
            "4. На выдохе потяните рукоять к животу.\n"
            "5. Сведите лопатки, задержитесь на секунду.\n"
            "6. На вдохе вернитесь в исходное положение, не округляя спину."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "cable_machine",
        "primary_muscles": ["latissimus_dorsi", "rhomboids"],
        "secondary_muscles": ["biceps", "trapezius", "erector_spinae"],
    },
    {
        "name": "Deadlift",
        "name_ru": "Становая тяга",
        "description_ru": "Базовое многосуставное упражнение для задней цепи мышц и общей силы.",
        "instructions_ru": (
            "1. Подойдите к штанге, стопы на ширине бёдер.\n"
            "2. Присядьте и возьмите штангу хватом на ширине плеч.\n"
            "3. Спина прямая, грудь расправлена, взгляд вперёд.\n"
            "4. На выдохе разогните ноги и корпус, поднимая штангу вдоль ног.\n"
            "5. В верхней точке полностью выпрямитесь.\n"
            "6. На вдохе опустите штангу по той же траектории.\n"
            "7. Не округляйте поясницу на протяжении всего движения."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["erector_spinae", "hamstrings", "glutes"],
        "secondary_muscles": ["quadriceps", "trapezius", "forearms", "latissimus_dorsi"],
    },
    {
        "name": "T-Bar Row",
        "name_ru": "Тяга Т-грифа",
        "description_ru": "Упражнение для развития толщины средней части спины.",
        "instructions_ru": (
            "1. Встаньте над Т-грифом, стопы на ширине плеч.\n"
            "2. Наклонитесь вперёд, возьмитесь за рукоять.\n"
            "3. Спина прямая, колени слегка согнуты.\n"
            "4. На выдохе подтяните гриф к груди.\n"
            "5. Сведите лопатки в верхней точке.\n"
            "6. На вдохе медленно опустите вес."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["latissimus_dorsi", "rhomboids"],
        "secondary_muscles": ["biceps", "trapezius", "erector_spinae"],
    },
    {
        "name": "Hyperextension",
        "name_ru": "Гиперэкстензия",
        "description_ru": "Упражнение для укрепления разгибателей спины и задней поверхности бедра.",
        "instructions_ru": (
            "1. Лягте на тренажёр для гиперэкстензии лицом вниз.\n"
            "2. Зафиксируйте ноги под валиками.\n"
            "3. Скрестите руки на груди или заведите за голову.\n"
            "4. На вдохе медленно наклонитесь вперёд.\n"
            "5. На выдохе разогнитесь до прямой линии с ногами.\n"
            "6. Не переразгибайте спину в верхней точке."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "bench",
        "primary_muscles": ["erector_spinae"],
        "secondary_muscles": ["glutes", "hamstrings"],
    },
    {
        "name": "Chin-Up",
        "name_ru": "Подтягивания обратным хватом",
        "description_ru": "Вариация подтягиваний с акцентом на бицепс и нижнюю часть широчайших.",
        "instructions_ru": (
            "1. Повисните на турнике обратным хватом (ладони к себе) на ширине плеч.\n"
            "2. На выдохе подтянитесь, стремясь подбородком выше перекладины.\n"
            "3. Сфокусируйтесь на работе мышц спины.\n"
            "4. На вдохе медленно опуститесь.\n"
            "5. Полностью выпрямляйте руки в нижней точке."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "pull_up_bar",
        "primary_muscles": ["latissimus_dorsi"],
        "secondary_muscles": ["biceps", "rhomboids"],
    },

    # ========================================================================
    # SHOULDERS (Плечи)
    # ========================================================================
    {
        "name": "Overhead Press",
        "name_ru": "Жим штанги стоя",
        "description_ru": "Базовое упражнение для развития дельтовидных мышц.",
        "instructions_ru": (
            "1. Возьмите штангу на грудь хватом чуть шире плеч.\n"
            "2. Стопы на ширине плеч, корпус прямой.\n"
            "3. На выдохе выжмите штангу вверх над головой.\n"
            "4. В верхней точке полностью выпрямите руки.\n"
            "5. На вдохе опустите штангу к верхней части груди.\n"
            "6. Не отклоняйте корпус назад."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["deltoid_anterior", "deltoid_lateral"],
        "secondary_muscles": ["triceps", "trapezius"],
    },
    {
        "name": "Dumbbell Lateral Raise",
        "name_ru": "Разведение гантелей в стороны",
        "description_ru": "Изолирующее упражнение для средней дельтовидной мышцы.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели в опущенных руках по бокам.\n"
            "2. Слегка согните локти и зафиксируйте их.\n"
            "3. На выдохе поднимите гантели в стороны до уровня плеч.\n"
            "4. В верхней точке мизинцы слегка выше больших пальцев.\n"
            "5. На вдохе медленно опустите гантели.\n"
            "6. Не раскачивайте корпус."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["deltoid_lateral"],
        "secondary_muscles": ["trapezius"],
    },
    {
        "name": "Dumbbell Front Raise",
        "name_ru": "Подъём гантелей перед собой",
        "description_ru": "Изолирующее упражнение для передней дельтовидной мышцы.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели перед бёдрами.\n"
            "2. На выдохе поднимите одну или обе гантели перед собой до уровня глаз.\n"
            "3. Локти слегка согнуты.\n"
            "4. На вдохе медленно опустите гантели.\n"
            "5. Не используйте инерцию тела."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["deltoid_anterior"],
        "secondary_muscles": ["pectoralis_major"],
    },
    {
        "name": "Rear Delt Fly",
        "name_ru": "Разведение гантелей в наклоне",
        "description_ru": "Изолирующее упражнение для задней дельтовидной мышцы.",
        "instructions_ru": (
            "1. Наклонитесь вперёд, спина прямая, угол 45–60 градусов.\n"
            "2. Гантели в опущенных руках, ладони друг к другу.\n"
            "3. На выдохе разведите гантели в стороны, сводя лопатки.\n"
            "4. Поднимите до уровня плеч.\n"
            "5. На вдохе медленно опустите гантели.\n"
            "6. Локти слегка согнуты на протяжении всего движения."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["deltoid_posterior"],
        "secondary_muscles": ["rhomboids", "trapezius"],
    },
    {
        "name": "Arnold Press",
        "name_ru": "Жим Арнольда",
        "description_ru": "Вариация жима гантелей с вращением, нагружающая все три пучка дельт.",
        "instructions_ru": (
            "1. Сядьте на скамью с вертикальной спинкой, гантели на уровне плеч.\n"
            "2. В начальном положении ладони обращены к себе.\n"
            "3. На выдохе выжимайте гантели вверх, одновременно разворачивая ладони наружу.\n"
            "4. В верхней точке ладони направлены от себя.\n"
            "5. На вдохе опустите гантели, разворачивая ладони обратно."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["deltoid_anterior", "deltoid_lateral"],
        "secondary_muscles": ["deltoid_posterior", "triceps"],
    },
    {
        "name": "Face Pull",
        "name_ru": "Тяга к лицу на верхнем блоке",
        "description_ru": "Упражнение для задних дельт и здоровья плечевых суставов.",
        "instructions_ru": (
            "1. Установите блок на уровне лица.\n"
            "2. Возьмите верёвочную рукоять двумя руками.\n"
            "3. Отойдите на шаг назад.\n"
            "4. На выдохе потяните рукоять к лицу, разводя руки в стороны.\n"
            "5. Сведите лопатки, разверните кисти наружу.\n"
            "6. На вдохе вернитесь в исходное положение."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "cable_machine",
        "primary_muscles": ["deltoid_posterior"],
        "secondary_muscles": ["rhomboids", "trapezius"],
    },
    {
        "name": "Dumbbell Shoulder Press",
        "name_ru": "Жим гантелей сидя",
        "description_ru": "Базовое упражнение для дельтовидных мышц с гантелями.",
        "instructions_ru": (
            "1. Сядьте на скамью с вертикальной спинкой.\n"
            "2. Поднимите гантели к уровню плеч, ладони вперёд.\n"
            "3. На выдохе выжмите гантели вверх.\n"
            "4. В верхней точке не ударяйте гантели друг о друга.\n"
            "5. На вдохе медленно опустите гантели к плечам."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["deltoid_anterior", "deltoid_lateral"],
        "secondary_muscles": ["triceps", "trapezius"],
    },
    {
        "name": "Barbell Upright Row",
        "name_ru": "Тяга штанги к подбородку",
        "description_ru": "Упражнение для развития дельтовидных и трапециевидных мышц.",
        "instructions_ru": (
            "1. Возьмите штангу узким хватом перед собой.\n"
            "2. На выдохе потяните штангу вверх вдоль тела.\n"
            "3. Локти ведите вверх и в стороны.\n"
            "4. Поднимите штангу до уровня подбородка.\n"
            "5. На вдохе медленно опустите штангу."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["deltoid_lateral", "trapezius"],
        "secondary_muscles": ["deltoid_anterior", "biceps"],
    },

    # ========================================================================
    # BICEPS (Бицепс)
    # ========================================================================
    {
        "name": "Barbell Curl",
        "name_ru": "Подъём штанги на бицепс",
        "description_ru": "Базовое упражнение для развития бицепса.",
        "instructions_ru": (
            "1. Встаньте прямо, возьмите штангу хватом снизу на ширине плеч.\n"
            "2. Прижмите локти к корпусу.\n"
            "3. На выдохе согните руки, поднимая штангу к плечам.\n"
            "4. Задержитесь на секунду в верхней точке.\n"
            "5. На вдохе медленно опустите штангу.\n"
            "6. Не раскачивайте корпус."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "barbell",
        "primary_muscles": ["biceps"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Dumbbell Curl",
        "name_ru": "Подъём гантелей на бицепс",
        "description_ru": "Упражнение для бицепса с возможностью супинации кисти.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели в опущенных руках, ладони к бёдрам.\n"
            "2. На выдохе согните руки, разворачивая ладони вверх (супинация).\n"
            "3. Поднимите гантели к плечам.\n"
            "4. На вдохе медленно опустите гантели.\n"
            "5. Можно выполнять поочерёдно или одновременно."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["biceps"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Hammer Curl",
        "name_ru": "Молотковые сгибания",
        "description_ru": "Упражнение для бицепса и брахиалиса нейтральным хватом.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели в руках нейтральным хватом (ладони друг к другу).\n"
            "2. Прижмите локти к корпусу.\n"
            "3. На выдохе согните руки, не разворачивая кисти.\n"
            "4. Поднимите гантели к плечам.\n"
            "5. На вдохе медленно опустите."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["biceps"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Preacher Curl",
        "name_ru": "Сгибания рук на скамье Скотта",
        "description_ru": "Изолирующее упражнение для бицепса с опорой на пюпитр.",
        "instructions_ru": (
            "1. Сядьте за скамью Скотта, упритесь трицепсами в подушку.\n"
            "2. Возьмите EZ-гриф хватом снизу.\n"
            "3. На выдохе согните руки, поднимая гриф.\n"
            "4. На вдохе медленно разогните руки.\n"
            "5. Не выпрямляйте руки до конца для сохранения напряжения."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "ez_bar",
        "primary_muscles": ["biceps"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Concentration Curl",
        "name_ru": "Концентрированные сгибания",
        "description_ru": "Изолирующее упражнение для пика бицепса.",
        "instructions_ru": (
            "1. Сядьте на скамью, ноги широко.\n"
            "2. Упритесь локтем рабочей руки во внутреннюю часть бедра.\n"
            "3. Возьмите гантель хватом снизу.\n"
            "4. На выдохе согните руку, поднимая гантель к плечу.\n"
            "5. Задержитесь на секунду, напрягая бицепс.\n"
            "6. На вдохе медленно опустите."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["biceps"],
        "secondary_muscles": [],
    },
    {
        "name": "Cable Bicep Curl",
        "name_ru": "Сгибания рук на нижнем блоке",
        "description_ru": "Упражнение для бицепса с постоянным напряжением от блока.",
        "instructions_ru": (
            "1. Встаньте перед нижним блоком, возьмите рукоять хватом снизу.\n"
            "2. Прижмите локти к корпусу.\n"
            "3. На выдохе согните руки, потянув рукоять к плечам.\n"
            "4. На вдохе медленно опустите.\n"
            "5. Сохраняйте неподвижность корпуса."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "cable_machine",
        "primary_muscles": ["biceps"],
        "secondary_muscles": ["forearms"],
    },

    # ========================================================================
    # TRICEPS (Трицепс)
    # ========================================================================
    {
        "name": "Close-Grip Bench Press",
        "name_ru": "Жим штанги узким хватом",
        "description_ru": "Базовое упражнение для трицепсов.",
        "instructions_ru": (
            "1. Лягте на горизонтальную скамью.\n"
            "2. Возьмите штангу узким хватом (руки на ширине плеч или уже).\n"
            "3. Снимите штангу со стоек.\n"
            "4. На вдохе опустите штангу к нижней части груди, прижимая локти к корпусу.\n"
            "5. На выдохе выжмите штангу вверх.\n"
            "6. Локти направлены вперёд, а не в стороны."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["triceps"],
        "secondary_muscles": ["pectoralis_major", "deltoid_anterior"],
    },
    {
        "name": "Tricep Pushdown",
        "name_ru": "Разгибание рук на верхнем блоке",
        "description_ru": "Изолирующее упражнение для трицепсов на блочном тренажёре.",
        "instructions_ru": (
            "1. Встаньте перед верхним блоком, возьмитесь за рукоять.\n"
            "2. Прижмите локти к корпусу, предплечья параллельны полу.\n"
            "3. На выдохе разогните руки, опустив рукоять вниз.\n"
            "4. Задержитесь на секунду в нижней точке.\n"
            "5. На вдохе медленно вернитесь в исходное положение.\n"
            "6. Двигаются только предплечья."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "cable_machine",
        "primary_muscles": ["triceps"],
        "secondary_muscles": [],
    },
    {
        "name": "Overhead Tricep Extension",
        "name_ru": "Французский жим гантели из-за головы",
        "description_ru": "Упражнение для длинной головки трицепса.",
        "instructions_ru": (
            "1. Сядьте или встаньте, возьмите гантель двумя руками.\n"
            "2. Поднимите гантель над головой, руки выпрямлены.\n"
            "3. На вдохе опустите гантель за голову, сгибая локти.\n"
            "4. Локти направлены вверх и прижаты к голове.\n"
            "5. На выдохе разогните руки, вернув гантель в верхнюю точку."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["triceps"],
        "secondary_muscles": [],
    },
    {
        "name": "Skull Crusher",
        "name_ru": "Французский жим лёжа",
        "description_ru": "Изолирующее упражнение для трицепсов лёжа на скамье.",
        "instructions_ru": (
            "1. Лягте на скамью, возьмите EZ-гриф узким хватом.\n"
            "2. Выпрямите руки вертикально над плечами.\n"
            "3. На вдохе согните руки в локтях, опуская гриф ко лбу.\n"
            "4. Локти неподвижны, направлены вверх.\n"
            "5. На выдохе разогните руки.\n"
            "6. Используйте контролируемый темп."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "ez_bar",
        "primary_muscles": ["triceps"],
        "secondary_muscles": [],
    },
    {
        "name": "Tricep Dips",
        "name_ru": "Отжимания на брусьях (трицепсовый вариант)",
        "description_ru": "Упражнение на брусьях с акцентом на трицепсы.",
        "instructions_ru": (
            "1. Примите упор на брусьях, руки выпрямлены.\n"
            "2. Корпус держите вертикально, ноги можно скрестить.\n"
            "3. На вдохе согните руки, прижимая локти к корпусу.\n"
            "4. Опускайтесь до прямого угла в локтях.\n"
            "5. На выдохе отожмитесь вверх.\n"
            "6. Не наклоняйте корпус вперёд."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "parallel_bars",
        "primary_muscles": ["triceps"],
        "secondary_muscles": ["pectoralis_major", "deltoid_anterior"],
    },
    {
        "name": "Dumbbell Kickback",
        "name_ru": "Разгибание руки с гантелью в наклоне",
        "description_ru": "Изолирующее упражнение для трицепса в наклоне.",
        "instructions_ru": (
            "1. Наклонитесь вперёд, одна рука упирается в скамью.\n"
            "2. Возьмите гантель, прижмите локоть к корпусу, предплечье вниз.\n"
            "3. На выдохе разогните руку назад до полного выпрямления.\n"
            "4. Задержитесь на секунду.\n"
            "5. На вдохе медленно верните руку в исходное положение."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["triceps"],
        "secondary_muscles": [],
    },

    # ========================================================================
    # LEGS (Ноги)
    # ========================================================================
    {
        "name": "Barbell Back Squat",
        "name_ru": "Приседания со штангой на плечах",
        "description_ru": "Базовое упражнение для развития мышц ног и ягодиц.",
        "instructions_ru": (
            "1. Расположите штангу на верхней части трапеций.\n"
            "2. Стопы на ширине плеч, носки слегка развёрнуты наружу.\n"
            "3. На вдохе присядьте, отводя таз назад.\n"
            "4. Опуститесь до параллели бёдер с полом или ниже.\n"
            "5. На выдохе встаньте, упираясь пятками в пол.\n"
            "6. Колени движутся в направлении носков, спина прямая."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "erector_spinae", "rectus_abdominis"],
    },
    {
        "name": "Front Squat",
        "name_ru": "Фронтальные приседания",
        "description_ru": "Вариация приседаний с акцентом на квадрицепс.",
        "instructions_ru": (
            "1. Расположите штангу на передних дельтах, скрестив руки.\n"
            "2. Локти направлены вперёд и вверх.\n"
            "3. Стопы на ширине плеч.\n"
            "4. На вдохе присядьте, сохраняя вертикальное положение корпуса.\n"
            "5. На выдохе встаньте.\n"
            "6. Не заваливайтесь вперёд."
        ),
        "difficulty": "advanced",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["quadriceps"],
        "secondary_muscles": ["glutes", "rectus_abdominis", "erector_spinae"],
    },
    {
        "name": "Leg Press",
        "name_ru": "Жим ногами в тренажёре",
        "description_ru": "Упражнение для ног в тренажёре с минимальной нагрузкой на спину.",
        "instructions_ru": (
            "1. Сядьте в тренажёр, прижмите спину к спинке.\n"
            "2. Поставьте стопы на платформу на ширине плеч.\n"
            "3. Снимите вес с упоров.\n"
            "4. На вдохе согните ноги, опуская платформу.\n"
            "5. Опустите до угла 90 градусов в коленях.\n"
            "6. На выдохе выжмите платформу, не выпрямляя колени до конца."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "leg_press",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings"],
    },
    {
        "name": "Leg Extension",
        "name_ru": "Разгибание ног в тренажёре",
        "description_ru": "Изолирующее упражнение для квадрицепса.",
        "instructions_ru": (
            "1. Сядьте в тренажёр, прижмите спину к спинке.\n"
            "2. Валик расположен на передней части голеней.\n"
            "3. На выдохе разогните ноги до полного выпрямления.\n"
            "4. Задержитесь на секунду в верхней точке.\n"
            "5. На вдохе медленно согните ноги."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "leg_extension",
        "primary_muscles": ["quadriceps"],
        "secondary_muscles": [],
    },
    {
        "name": "Leg Curl",
        "name_ru": "Сгибание ног в тренажёре",
        "description_ru": "Изолирующее упражнение для бицепса бедра.",
        "instructions_ru": (
            "1. Лягте на тренажёр лицом вниз.\n"
            "2. Валик расположен на задней части голеней.\n"
            "3. На выдохе согните ноги, подтягивая валик к ягодицам.\n"
            "4. Задержитесь на секунду.\n"
            "5. На вдохе медленно разогните ноги."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "leg_curl",
        "primary_muscles": ["hamstrings"],
        "secondary_muscles": ["calves"],
    },
    {
        "name": "Romanian Deadlift",
        "name_ru": "Румынская тяга",
        "description_ru": "Упражнение для задней поверхности бедра и ягодиц.",
        "instructions_ru": (
            "1. Возьмите штангу хватом на ширине плеч, встаньте прямо.\n"
            "2. Колени слегка согнуты и зафиксированы.\n"
            "3. На вдохе наклонитесь вперёд, отводя таз назад.\n"
            "4. Опустите штангу вдоль ног до середины голени.\n"
            "5. Почувствуйте растяжение задней поверхности бедра.\n"
            "6. На выдохе вернитесь в исходное положение.\n"
            "7. Спина прямая на протяжении всего движения."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["hamstrings", "glutes"],
        "secondary_muscles": ["erector_spinae"],
    },
    {
        "name": "Walking Lunge",
        "name_ru": "Выпады с гантелями",
        "description_ru": "Упражнение для ног и ягодиц, развивающее координацию и баланс.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели в опущенных руках.\n"
            "2. Сделайте широкий шаг вперёд.\n"
            "3. На вдохе опуститесь, сгибая обе ноги до 90 градусов.\n"
            "4. Заднее колено почти касается пола.\n"
            "5. На выдохе оттолкнитесь передней ногой и сделайте следующий шаг.\n"
            "6. Корпус держите вертикально."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "calves"],
    },
    {
        "name": "Bulgarian Split Squat",
        "name_ru": "Болгарские сплит-приседания",
        "description_ru": "Одностороннее упражнение для ног с задней ногой на возвышении.",
        "instructions_ru": (
            "1. Встаньте спиной к скамье на расстоянии большого шага.\n"
            "2. Положите подъём задней ноги на скамью.\n"
            "3. Гантели в опущенных руках или штанга на плечах.\n"
            "4. На вдохе присядьте на передней ноге.\n"
            "5. Опуститесь до параллели бедра с полом.\n"
            "6. На выдохе встаньте, упираясь передней ногой."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "adductors"],
    },
    {
        "name": "Standing Calf Raise",
        "name_ru": "Подъём на носки стоя",
        "description_ru": "Изолирующее упражнение для икроножных мышц.",
        "instructions_ru": (
            "1. Встаньте носками на край платформы или ступеньки.\n"
            "2. Пятки свисают, вес тела на подушечках стоп.\n"
            "3. На выдохе поднимитесь на носки как можно выше.\n"
            "4. Задержитесь на секунду в верхней точке.\n"
            "5. На вдохе медленно опуститесь, растягивая икры.\n"
            "6. Можно использовать гантели или штангу для утяжеления."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["calves"],
        "secondary_muscles": [],
    },
    {
        "name": "Hip Thrust",
        "name_ru": "Ягодичный мост со штангой",
        "description_ru": "Упражнение для максимальной активации ягодичных мышц.",
        "instructions_ru": (
            "1. Сядьте на пол, лопатками обопритесь о скамью.\n"
            "2. Положите штангу на бёдра (используйте подкладку).\n"
            "3. Стопы на полу, колени согнуты под 90 градусов.\n"
            "4. На выдохе поднимите таз, сжимая ягодицы.\n"
            "5. В верхней точке тело от плеч до колен — прямая линия.\n"
            "6. На вдохе опустите таз."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["glutes"],
        "secondary_muscles": ["hamstrings", "quadriceps"],
    },
    {
        "name": "Goblet Squat",
        "name_ru": "Приседания с гантелью у груди",
        "description_ru": "Вариация приседаний для начинающих с гантелью у груди.",
        "instructions_ru": (
            "1. Возьмите гантель за один конец, держите у груди.\n"
            "2. Стопы чуть шире плеч, носки слегка наружу.\n"
            "3. На вдохе присядьте, разводя колени в стороны.\n"
            "4. Опуститесь как можно глубже, спина прямая.\n"
            "5. На выдохе встаньте.\n"
            "6. Локти находятся между коленями в нижней точке."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "rectus_abdominis"],
    },
    {
        "name": "Sumo Deadlift",
        "name_ru": "Тяга сумо",
        "description_ru": "Вариация становой тяги с широкой постановкой ног.",
        "instructions_ru": (
            "1. Встаньте в широкую стойку, носки развёрнуты наружу на 45 градусов.\n"
            "2. Присядьте и возьмите штангу узким хватом между ног.\n"
            "3. Спина прямая, грудь расправлена.\n"
            "4. На выдохе выпрямите ноги и корпус.\n"
            "5. На вдохе опустите штангу.\n"
            "6. Колени следуют за направлением носков."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["quadriceps", "glutes", "adductors"],
        "secondary_muscles": ["hamstrings", "erector_spinae", "trapezius"],
    },
    {
        "name": "Step-Up",
        "name_ru": "Зашагивания на платформу",
        "description_ru": "Функциональное упражнение для ног и ягодиц.",
        "instructions_ru": (
            "1. Встаньте перед скамьёй или платформой с гантелями в руках.\n"
            "2. Поставьте одну ногу на платформу.\n"
            "3. На выдохе зашагните, выпрямив опорную ногу.\n"
            "4. На вдохе медленно опуститесь.\n"
            "5. Выполните все повторения на одну ногу, затем на другую."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "calves"],
    },
    {
        "name": "Seated Calf Raise",
        "name_ru": "Подъём на носки сидя",
        "description_ru": "Изолирующее упражнение для камбаловидной мышцы.",
        "instructions_ru": (
            "1. Сядьте в тренажёр для подъёма на носки.\n"
            "2. Поставьте подушечки стоп на платформу.\n"
            "3. Подушка тренажёра — на бёдрах чуть выше колен.\n"
            "4. На выдохе поднимитесь на носки.\n"
            "5. Задержитесь на секунду.\n"
            "6. На вдохе медленно опустите пятки."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "bench",
        "primary_muscles": ["calves"],
        "secondary_muscles": [],
    },

    # ========================================================================
    # CORE (Кор / Пресс)
    # ========================================================================
    {
        "name": "Crunch",
        "name_ru": "Скручивания",
        "description_ru": "Базовое упражнение для прямой мышцы живота.",
        "instructions_ru": (
            "1. Лягте на спину, колени согнуты, стопы на полу.\n"
            "2. Руки за головой или скрещены на груди.\n"
            "3. На выдохе оторвите лопатки от пола, скручивая корпус.\n"
            "4. Не тяните себя руками за шею.\n"
            "5. На вдохе медленно вернитесь.\n"
            "6. Поясница остаётся прижатой к полу."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["rectus_abdominis"],
        "secondary_muscles": [],
    },
    {
        "name": "Plank",
        "name_ru": "Планка",
        "description_ru": "Статическое упражнение для укрепления всего кора.",
        "instructions_ru": (
            "1. Примите упор на предплечьях и носках.\n"
            "2. Тело образует прямую линию от головы до пят.\n"
            "3. Напрягите мышцы живота и ягодиц.\n"
            "4. Не прогибайте и не поднимайте поясницу.\n"
            "5. Удерживайте положение заданное время.\n"
            "6. Дышите ровно, не задерживайте дыхание."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["rectus_abdominis", "transverse_abdominis"],
        "secondary_muscles": ["obliques", "erector_spinae"],
    },
    {
        "name": "Russian Twist",
        "name_ru": "Русские скручивания",
        "description_ru": "Упражнение для косых мышц живота с ротацией корпуса.",
        "instructions_ru": (
            "1. Сядьте на пол, колени согнуты, стопы на полу или на весу.\n"
            "2. Отклоните корпус назад на 45 градусов.\n"
            "3. Руки вместе перед собой (можно с медболом или гантелью).\n"
            "4. На выдохе повернитесь в одну сторону.\n"
            "5. На вдохе вернитесь в центр.\n"
            "6. Повторите в другую сторону."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["obliques"],
        "secondary_muscles": ["rectus_abdominis"],
    },
    {
        "name": "Hanging Leg Raise",
        "name_ru": "Подъём ног в висе",
        "description_ru": "Упражнение для нижней части пресса в висе на турнике.",
        "instructions_ru": (
            "1. Повисните на турнике прямым хватом.\n"
            "2. Ноги прямые, тело неподвижно.\n"
            "3. На выдохе поднимите прямые ноги до параллели с полом.\n"
            "4. Задержитесь на секунду.\n"
            "5. На вдохе медленно опустите ноги.\n"
            "6. Не раскачивайтесь."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "pull_up_bar",
        "primary_muscles": ["rectus_abdominis"],
        "secondary_muscles": ["hip_flexors", "obliques"],
    },
    {
        "name": "Ab Wheel Rollout",
        "name_ru": "Ролик для пресса",
        "description_ru": "Продвинутое упражнение для всего кора с роликом.",
        "instructions_ru": (
            "1. Встаньте на колени, возьмите ролик обеими руками.\n"
            "2. Ролик перед собой на полу.\n"
            "3. На вдохе прокатите ролик вперёд, растягивая тело.\n"
            "4. Опуститесь как можно ниже, не касаясь пола.\n"
            "5. На выдохе напрягите пресс и вернитесь в исходное положение.\n"
            "6. Не прогибайте поясницу."
        ),
        "difficulty": "advanced",
        "exercise_type": "compound",
        "equipment_name": "ab_wheel",
        "primary_muscles": ["rectus_abdominis", "transverse_abdominis"],
        "secondary_muscles": ["obliques", "erector_spinae", "latissimus_dorsi"],
    },
    {
        "name": "Bicycle Crunch",
        "name_ru": "Велосипедные скручивания",
        "description_ru": "Динамическое упражнение для прямой и косых мышц живота.",
        "instructions_ru": (
            "1. Лягте на спину, руки за головой.\n"
            "2. Поднимите ноги, согнув колени под 90 градусов.\n"
            "3. На выдохе скрутите корпус, направляя правый локоть к левому колену.\n"
            "4. Одновременно выпрямите правую ногу.\n"
            "5. Повторите в другую сторону.\n"
            "6. Движение плавное, без рывков."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["rectus_abdominis", "obliques"],
        "secondary_muscles": ["hip_flexors"],
    },
    {
        "name": "Side Plank",
        "name_ru": "Боковая планка",
        "description_ru": "Статическое упражнение для косых мышц живота.",
        "instructions_ru": (
            "1. Лягте на бок, обопритесь на предплечье.\n"
            "2. Поднимите таз, тело образует прямую линию.\n"
            "3. Верхнюю руку положите на бок или поднимите вверх.\n"
            "4. Удерживайте положение заданное время.\n"
            "5. Не проваливайте таз.\n"
            "6. Повторите на другую сторону."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["obliques"],
        "secondary_muscles": ["transverse_abdominis", "glutes"],
    },
    {
        "name": "Dead Bug",
        "name_ru": "Мёртвый жук",
        "description_ru": "Упражнение для стабилизации кора и координации.",
        "instructions_ru": (
            "1. Лягте на спину, поднимите руки вертикально.\n"
            "2. Ноги согнуты под 90 градусов (голени параллельны полу).\n"
            "3. Прижмите поясницу к полу.\n"
            "4. Медленно опустите правую руку за голову и выпрямите левую ногу.\n"
            "5. Вернитесь в исходное положение.\n"
            "6. Повторите с другой стороны.\n"
            "7. Поясница остаётся прижатой на протяжении всего движения."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["transverse_abdominis", "rectus_abdominis"],
        "secondary_muscles": ["hip_flexors"],
    },
    {
        "name": "Cable Woodchop",
        "name_ru": "Дровосек на блоке",
        "description_ru": "Ротационное упражнение для косых мышц на блочном тренажёре.",
        "instructions_ru": (
            "1. Установите блок в верхнее положение.\n"
            "2. Встаньте боком к тренажёру.\n"
            "3. Возьмите рукоять обеими руками.\n"
            "4. На выдохе потяните рукоять диагонально вниз, поворачивая корпус.\n"
            "5. Руки прямые, движение идёт от корпуса.\n"
            "6. На вдохе вернитесь в исходное положение."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "cable_machine",
        "primary_muscles": ["obliques"],
        "secondary_muscles": ["rectus_abdominis", "transverse_abdominis"],
    },
    {
        "name": "Lying Leg Raise",
        "name_ru": "Подъём ног лёжа",
        "description_ru": "Упражнение для нижней части пресса лёжа на полу.",
        "instructions_ru": (
            "1. Лягте на спину, руки вдоль тела или под ягодицами.\n"
            "2. Ноги прямые, вместе.\n"
            "3. На выдохе поднимите ноги до вертикального положения.\n"
            "4. На вдохе медленно опустите ноги, не касаясь пола.\n"
            "5. Поясница прижата к полу.\n"
            "6. Если сложно — слегка согните колени."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["rectus_abdominis"],
        "secondary_muscles": ["hip_flexors"],
    },

    # ========================================================================
    # CARDIO (Кардио)
    # ========================================================================
    {
        "name": "Running",
        "name_ru": "Бег",
        "description_ru": "Основная кардионагрузка для улучшения выносливости и сжигания калорий.",
        "instructions_ru": (
            "1. Начните с разминочной ходьбы 3–5 минут.\n"
            "2. Постепенно увеличьте темп до комфортного бега.\n"
            "3. Дышите ритмично, приземляйтесь на среднюю часть стопы.\n"
            "4. Корпус слегка наклонён вперёд.\n"
            "5. Руки согнуты под 90 градусов, двигаются вдоль тела.\n"
            "6. Завершите заминкой с постепенным замедлением."
        ),
        "difficulty": "beginner",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["quadriceps", "hamstrings", "calves"],
        "secondary_muscles": ["glutes", "hip_flexors", "rectus_abdominis"],
    },
    {
        "name": "Rowing Machine",
        "name_ru": "Гребля на тренажёре",
        "description_ru": "Кардиоупражнение, задействующее всё тело.",
        "instructions_ru": (
            "1. Сядьте на тренажёр, зафиксируйте стопы.\n"
            "2. Возьмитесь за рукоять, руки вытянуты.\n"
            "3. Оттолкнитесь ногами, затем подтяните рукоять к животу.\n"
            "4. Разогните руки, наклонитесь вперёд, согните ноги.\n"
            "5. Движение: ноги — корпус — руки (тяга), руки — корпус — ноги (возврат).\n"
            "6. Сохраняйте ровный ритм."
        ),
        "difficulty": "beginner",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["latissimus_dorsi", "quadriceps"],
        "secondary_muscles": ["biceps", "erector_spinae", "glutes", "hamstrings"],
    },
    {
        "name": "Burpee",
        "name_ru": "Бёрпи",
        "description_ru": "Высокоинтенсивное упражнение для всего тела.",
        "instructions_ru": (
            "1. Встаньте прямо, стопы на ширине плеч.\n"
            "2. Присядьте, упритесь руками в пол.\n"
            "3. Прыжком отведите ноги назад — примите упор лёжа.\n"
            "4. Выполните одно отжимание (опционально).\n"
            "5. Прыжком подтяните ноги к рукам.\n"
            "6. Выпрыгните вверх, хлопнув руками над головой."
        ),
        "difficulty": "intermediate",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["quadriceps", "pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps", "rectus_abdominis", "glutes"],
    },
    {
        "name": "Jumping Jack",
        "name_ru": "Прыжки с разведением рук и ног",
        "description_ru": "Простое кардиоупражнение для разминки и повышения пульса.",
        "instructions_ru": (
            "1. Встаньте прямо, ноги вместе, руки вдоль тела.\n"
            "2. Прыжком разведите ноги в стороны и поднимите руки над головой.\n"
            "3. Следующим прыжком вернитесь в исходное положение.\n"
            "4. Выполняйте в быстром темпе.\n"
            "5. Приземляйтесь мягко, на подушечки стоп."
        ),
        "difficulty": "beginner",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["calves", "deltoid_lateral"],
        "secondary_muscles": ["quadriceps", "glutes"],
    },
    {
        "name": "Mountain Climber",
        "name_ru": "Скалолаз",
        "description_ru": "Динамическое кардиоупражнение в упоре лёжа.",
        "instructions_ru": (
            "1. Примите упор лёжа, руки прямые.\n"
            "2. Поочерёдно подтягивайте колени к груди.\n"
            "3. Сохраняйте ровное положение корпуса.\n"
            "4. Выполняйте в быстром темпе.\n"
            "5. Дышите ритмично.\n"
            "6. Не поднимайте таз слишком высоко."
        ),
        "difficulty": "beginner",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["rectus_abdominis", "hip_flexors"],
        "secondary_muscles": ["quadriceps", "deltoid_anterior", "pectoralis_major"],
    },
    {
        "name": "Jump Rope",
        "name_ru": "Прыжки со скакалкой",
        "description_ru": "Классическое кардиоупражнение для развития координации и выносливости.",
        "instructions_ru": (
            "1. Возьмите скакалку, рукоятки на уровне бёдер.\n"
            "2. Вращайте скакалку кистями, а не всеми руками.\n"
            "3. Прыгайте невысоко, приземляясь на подушечки стоп.\n"
            "4. Колени слегка согнуты.\n"
            "5. Спина прямая, взгляд вперёд.\n"
            "6. Начинайте с 1–2 минут, постепенно увеличивая время."
        ),
        "difficulty": "beginner",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["calves"],
        "secondary_muscles": ["quadriceps", "glutes", "forearms"],
    },

    # ========================================================================
    # ADDITIONAL COMPOUND / FUNCTIONAL (Дополнительные)
    # ========================================================================
    {
        "name": "Kettlebell Swing",
        "name_ru": "Махи гирей",
        "description_ru": "Взрывное упражнение для задней цепи и кардиовыносливости.",
        "instructions_ru": (
            "1. Встаньте в широкую стойку, гиря на полу перед вами.\n"
            "2. Наклонитесь, возьмите гирю обеими руками.\n"
            "3. Качните гирю между ног (как маятник).\n"
            "4. Мощным движением бёдер вытолкните гирю вперёд до уровня плеч.\n"
            "5. Руки расслаблены — движение идёт от бёдер.\n"
            "6. Позвольте гире вернуться между ног и повторите."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "kettlebell",
        "primary_muscles": ["glutes", "hamstrings"],
        "secondary_muscles": ["erector_spinae", "deltoid_anterior", "rectus_abdominis"],
    },
    {
        "name": "Kettlebell Goblet Squat",
        "name_ru": "Приседания с гирей у груди",
        "description_ru": "Приседания с гирей для проработки ног и кора.",
        "instructions_ru": (
            "1. Возьмите гирю за рога (ручки), прижмите к груди.\n"
            "2. Стопы чуть шире плеч, носки слегка развёрнуты.\n"
            "3. На вдохе присядьте глубоко, разводя колени.\n"
            "4. Локти между коленями в нижней точке.\n"
            "5. На выдохе встаньте.\n"
            "6. Спина прямая на протяжении всего движения."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "kettlebell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "rectus_abdominis"],
    },
    {
        "name": "Barbell Shrug",
        "name_ru": "Шраги со штангой",
        "description_ru": "Изолирующее упражнение для верхней части трапециевидных мышц.",
        "instructions_ru": (
            "1. Встаньте прямо, штанга в опущенных руках перед собой.\n"
            "2. На выдохе поднимите плечи как можно выше к ушам.\n"
            "3. Задержитесь на секунду в верхней точке.\n"
            "4. На вдохе медленно опустите плечи.\n"
            "5. Не вращайте плечами — движение строго вверх-вниз.\n"
            "6. Руки остаются прямыми."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "barbell",
        "primary_muscles": ["trapezius"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Dumbbell Shrug",
        "name_ru": "Шраги с гантелями",
        "description_ru": "Упражнение для трапециевидных мышц с гантелями.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели в опущенных руках по бокам.\n"
            "2. На выдохе поднимите плечи как можно выше.\n"
            "3. Задержитесь на секунду.\n"
            "4. На вдохе медленно опустите.\n"
            "5. Держите руки прямыми."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["trapezius"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Wrist Curl",
        "name_ru": "Сгибание запястий со штангой",
        "description_ru": "Изолирующее упражнение для сгибателей предплечья.",
        "instructions_ru": (
            "1. Сядьте на скамью, предплечья на бёдрах, кисти свисают.\n"
            "2. Возьмите штангу хватом снизу.\n"
            "3. На выдохе согните запястья, поднимая штангу.\n"
            "4. На вдохе медленно опустите.\n"
            "5. Предплечья остаются неподвижными."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "barbell",
        "primary_muscles": ["forearms"],
        "secondary_muscles": [],
    },
    {
        "name": "Reverse Wrist Curl",
        "name_ru": "Разгибание запястий со штангой",
        "description_ru": "Изолирующее упражнение для разгибателей предплечья.",
        "instructions_ru": (
            "1. Сядьте на скамью, предплечья на бёдрах, кисти свисают.\n"
            "2. Возьмите штангу хватом сверху.\n"
            "3. На выдохе разогните запястья, поднимая штангу.\n"
            "4. На вдохе медленно опустите.\n"
            "5. Используйте лёгкий вес."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "barbell",
        "primary_muscles": ["forearms"],
        "secondary_muscles": [],
    },
    {
        "name": "Smith Machine Squat",
        "name_ru": "Приседания в машине Смита",
        "description_ru": "Приседания в тренажёре с направляющими для безопасности.",
        "instructions_ru": (
            "1. Встаньте под гриф машины Смита, расположив его на трапециях.\n"
            "2. Стопы чуть впереди, на ширине плеч.\n"
            "3. Разблокируйте гриф.\n"
            "4. На вдохе присядьте до параллели.\n"
            "5. На выдохе встаньте.\n"
            "6. Заблокируйте гриф после завершения подхода."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "smith_machine",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings"],
    },
    {
        "name": "Machine Chest Press",
        "name_ru": "Жим от груди в тренажёре",
        "description_ru": "Безопасная альтернатива жиму штанги для начинающих.",
        "instructions_ru": (
            "1. Сядьте в тренажёр, прижмите спину к спинке.\n"
            "2. Возьмитесь за рукоятки на уровне груди.\n"
            "3. На выдохе выжмите рукоятки от себя.\n"
            "4. На вдохе медленно вернитесь.\n"
            "5. Не выпрямляйте руки полностью в конечной точке."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "chest_press_machine",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior", "triceps"],
    },
    {
        "name": "Cable Lateral Raise",
        "name_ru": "Отведение руки в сторону на нижнем блоке",
        "description_ru": "Изолирующее упражнение для средней дельты с постоянным напряжением.",
        "instructions_ru": (
            "1. Встаньте боком к нижнему блоку.\n"
            "2. Дальней рукой возьмите рукоять.\n"
            "3. На выдохе поднимите руку в сторону до уровня плеча.\n"
            "4. Локоть слегка согнут.\n"
            "5. На вдохе медленно опустите.\n"
            "6. Выполните на обе стороны."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "cable_machine",
        "primary_muscles": ["deltoid_lateral"],
        "secondary_muscles": [],
    },
    {
        "name": "TRX Row",
        "name_ru": "Тяга на TRX петлях",
        "description_ru": "Упражнение для спины с собственным весом на петлях.",
        "instructions_ru": (
            "1. Возьмитесь за рукоятки TRX, отклонитесь назад.\n"
            "2. Тело прямое, пятки на полу.\n"
            "3. На выдохе подтяните грудь к рукояткам.\n"
            "4. Сведите лопатки.\n"
            "5. На вдохе вернитесь в исходное положение.\n"
            "6. Чем ниже угол тела — тем сложнее упражнение."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "trx",
        "primary_muscles": ["latissimus_dorsi", "rhomboids"],
        "secondary_muscles": ["biceps", "trapezius", "rectus_abdominis"],
    },
    {
        "name": "Resistance Band Pull-Apart",
        "name_ru": "Разведение рук с резиновой лентой",
        "description_ru": "Упражнение для задних дельт и здоровья плеч.",
        "instructions_ru": (
            "1. Возьмите ленту на ширине плеч перед собой.\n"
            "2. Руки прямые, лента натянута.\n"
            "3. На выдохе разведите руки в стороны, растягивая ленту.\n"
            "4. Сведите лопатки.\n"
            "5. На вдохе вернитесь.\n"
            "6. Плечи опущены на протяжении движения."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "resistance_band",
        "primary_muscles": ["deltoid_posterior", "rhomboids"],
        "secondary_muscles": ["trapezius"],
    },
    {
        "name": "Medicine Ball Slam",
        "name_ru": "Удары медицинским мячом об пол",
        "description_ru": "Взрывное упражнение для всего тела и кардио.",
        "instructions_ru": (
            "1. Встаньте прямо, мяч в руках над головой.\n"
            "2. Поднимитесь на носки, полностью вытянувшись.\n"
            "3. С силой бросьте мяч об пол перед собой.\n"
            "4. Присядьте, подберите мяч.\n"
            "5. Вернитесь в исходное положение.\n"
            "6. Повторите в быстром темпе."
        ),
        "difficulty": "intermediate",
        "exercise_type": "cardio",
        "equipment_name": "medicine_ball",
        "primary_muscles": ["rectus_abdominis", "latissimus_dorsi"],
        "secondary_muscles": ["deltoid_anterior", "quadriceps", "glutes"],
    },
    {
        "name": "Hip Adduction Machine",
        "name_ru": "Сведение ног в тренажёре",
        "description_ru": "Изолирующее упражнение для приводящих мышц бедра.",
        "instructions_ru": (
            "1. Сядьте в тренажёр, прижмите спину к спинке.\n"
            "2. Ноги разведены, упираются в подушки.\n"
            "3. На выдохе сведите ноги вместе.\n"
            "4. Задержитесь на секунду.\n"
            "5. На вдохе медленно вернитесь в исходное положение.\n"
            "6. Контролируйте движение, не используйте инерцию."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["adductors"],
        "secondary_muscles": [],
    },
    {
        "name": "Hip Abduction Machine",
        "name_ru": "Разведение ног в тренажёре",
        "description_ru": "Изолирующее упражнение для отводящих мышц бедра.",
        "instructions_ru": (
            "1. Сядьте в тренажёр, прижмите спину к спинке.\n"
            "2. Ноги вместе, упираются в подушки.\n"
            "3. На выдохе разведите ноги в стороны.\n"
            "4. Задержитесь на секунду.\n"
            "5. На вдохе медленно сведите ноги.\n"
            "6. Не разводите ноги рывком."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": None,
        "primary_muscles": ["abductors"],
        "secondary_muscles": ["glutes"],
    },
    {
        "name": "Dumbbell Fly",
        "name_ru": "Разведение гантелей лёжа",
        "description_ru": "Изолирующее упражнение для растяжения и проработки грудных мышц.",
        "instructions_ru": (
            "1. Лягте на горизонтальную скамью с гантелями.\n"
            "2. Выжмите гантели вверх, ладони друг к другу.\n"
            "3. Слегка согните локти и зафиксируйте.\n"
            "4. На вдохе разведите руки в стороны дугой.\n"
            "5. Опустите до ощущения растяжения в грудных мышцах.\n"
            "6. На выдохе сведите руки обратно."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["pectoralis_major"],
        "secondary_muscles": ["deltoid_anterior"],
    },
    {
        "name": "Good Morning",
        "name_ru": "Гуд-морнинг (наклоны со штангой)",
        "description_ru": "Упражнение для разгибателей спины и задней поверхности бедра.",
        "instructions_ru": (
            "1. Положите штангу на верхнюю часть трапеций.\n"
            "2. Стопы на ширине плеч, колени слегка согнуты.\n"
            "3. На вдохе наклонитесь вперёд, отводя таз назад.\n"
            "4. Наклонитесь до параллели корпуса с полом.\n"
            "5. На выдохе вернитесь в вертикальное положение.\n"
            "6. Спина прямая на протяжении всего движения."
        ),
        "difficulty": "intermediate",
        "exercise_type": "compound",
        "equipment_name": "barbell",
        "primary_muscles": ["erector_spinae", "hamstrings"],
        "secondary_muscles": ["glutes"],
    },
    {
        "name": "Reverse Lunge",
        "name_ru": "Обратные выпады",
        "description_ru": "Вариация выпадов с шагом назад, более щадящая для коленей.",
        "instructions_ru": (
            "1. Встаньте прямо, гантели в руках или штанга на плечах.\n"
            "2. Сделайте широкий шаг назад.\n"
            "3. На вдохе опуститесь, сгибая обе ноги до 90 градусов.\n"
            "4. Заднее колено почти касается пола.\n"
            "5. На выдохе вернитесь в исходное положение.\n"
            "6. Чередуйте ноги."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings", "calves"],
    },
    {
        "name": "Farmer's Walk",
        "name_ru": "Прогулка фермера",
        "description_ru": "Функциональное упражнение для силы хвата, кора и всего тела.",
        "instructions_ru": (
            "1. Возьмите тяжёлые гантели или гири в обе руки.\n"
            "2. Встаньте прямо, плечи расправлены.\n"
            "3. Идите вперёд ровным шагом.\n"
            "4. Сохраняйте прямую осанку.\n"
            "5. Пройдите заданное расстояние или время.\n"
            "6. Аккуратно поставьте вес на пол."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "dumbbell",
        "primary_muscles": ["forearms", "trapezius"],
        "secondary_muscles": ["rectus_abdominis", "obliques", "erector_spinae"],
    },
    {
        "name": "Lat Pulldown Close Grip",
        "name_ru": "Тяга верхнего блока узким хватом",
        "description_ru": "Вариация тяги верхнего блока с акцентом на нижнюю часть широчайших.",
        "instructions_ru": (
            "1. Сядьте за тренажёр, зафиксируйте бёдра.\n"
            "2. Возьмите V-образную рукоять.\n"
            "3. На выдохе потяните рукоять к верхней части груди.\n"
            "4. Сведите лопатки, локти вдоль корпуса.\n"
            "5. На вдохе вернитесь.\n"
            "6. Не раскачивайте корпус."
        ),
        "difficulty": "beginner",
        "exercise_type": "compound",
        "equipment_name": "lat_pulldown",
        "primary_muscles": ["latissimus_dorsi"],
        "secondary_muscles": ["biceps", "rhomboids"],
    },
    {
        "name": "EZ Bar Curl",
        "name_ru": "Подъём EZ-грифа на бицепс",
        "description_ru": "Упражнение для бицепса с изогнутым грифом, снижающим нагрузку на запястья.",
        "instructions_ru": (
            "1. Возьмите EZ-гриф за изогнутые части хватом снизу.\n"
            "2. Встаньте прямо, локти прижаты к корпусу.\n"
            "3. На выдохе согните руки, поднимая гриф к плечам.\n"
            "4. На вдохе медленно опустите.\n"
            "5. Не раскачивайте корпус."
        ),
        "difficulty": "beginner",
        "exercise_type": "isolation",
        "equipment_name": "ez_bar",
        "primary_muscles": ["biceps"],
        "secondary_muscles": ["forearms"],
    },
    {
        "name": "Incline Dumbbell Curl",
        "name_ru": "Сгибания рук с гантелями на наклонной скамье",
        "description_ru": "Упражнение для бицепса с увеличенной амплитудой и растяжением.",
        "instructions_ru": (
            "1. Сядьте на наклонную скамью (45 градусов), гантели в опущенных руках.\n"
            "2. Руки свисают вертикально вниз.\n"
            "3. На выдохе согните руки, поднимая гантели.\n"
            "4. На вдохе медленно опустите с полной амплитудой.\n"
            "5. Локти неподвижны, прижаты к корпусу."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["biceps"],
        "secondary_muscles": [],
    },
    {
        "name": "Dumbbell Pullover",
        "name_ru": "Пуловер с гантелью",
        "description_ru": "Упражнение для грудных и широчайших мышц.",
        "instructions_ru": (
            "1. Лягте поперёк скамьи, опираясь верхней частью спины.\n"
            "2. Возьмите гантель обеими руками, поднимите над грудью.\n"
            "3. На вдохе опустите гантель за голову дугообразным движением.\n"
            "4. Почувствуйте растяжение в грудных и широчайших.\n"
            "5. На выдохе верните гантель в исходное положение.\n"
            "6. Руки слегка согнуты в локтях."
        ),
        "difficulty": "intermediate",
        "exercise_type": "isolation",
        "equipment_name": "dumbbell",
        "primary_muscles": ["pectoralis_major", "latissimus_dorsi"],
        "secondary_muscles": ["triceps"],
    },
    {
        "name": "Box Jump",
        "name_ru": "Запрыгивания на тумбу",
        "description_ru": "Плиометрическое упражнение для взрывной силы ног.",
        "instructions_ru": (
            "1. Встаньте перед тумбой, стопы на ширине плеч.\n"
            "2. Присядьте и замахните руками назад.\n"
            "3. Взрывным движением запрыгните на тумбу.\n"
            "4. Приземлитесь мягко на всю стопу, слегка присев.\n"
            "5. Выпрямитесь на тумбе.\n"
            "6. Спуститесь шагом вниз (не спрыгивайте для безопасности)."
        ),
        "difficulty": "intermediate",
        "exercise_type": "cardio",
        "equipment_name": None,
        "primary_muscles": ["quadriceps", "glutes", "calves"],
        "secondary_muscles": ["hamstrings", "hip_flexors"],
    },
]

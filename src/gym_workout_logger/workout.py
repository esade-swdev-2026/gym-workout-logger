from dataclasses import dataclass


def normalize_exercise_name(name: str) -> str:
    return name.strip()


def normalize_muscle_group(muscle_group: str) -> str:
    return muscle_group.strip()


def is_valid_exercise_name(name: str) -> bool:
    return bool(name.strip())


def is_valid_muscle_group(muscle_group: str) -> bool:
    return bool(muscle_group.strip())


@dataclass(frozen=True)
class Exercise:
    name: str
    muscle_group: str


def create_exercise(name: str, muscle_group: str) -> Exercise:
    return Exercise(
        name=normalize_exercise_name(name),
        muscle_group=normalize_muscle_group(muscle_group),
    )

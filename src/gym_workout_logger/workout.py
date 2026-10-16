"""Workout data and calculations. No file reading or printing here."""

from dataclasses import dataclass
from math import isfinite


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


@dataclass(frozen=True)
class Workout:
    workout_id: int


@dataclass(frozen=True)
class WorkoutSet:
    exercise_name: str
    reps: int
    weight: float
    workout_id: int


@dataclass(frozen=True)
class ExerciseSummary:
    name: str
    muscle_group: str
    total_sets: int
    total_reps: int
    total_volume: float


def is_valid_reps(reps: int) -> bool:
    return reps > 0


def is_valid_weight(weight: float) -> bool:
    return isfinite(weight) and weight >= 0.0


def find_exercise(exercises: list[Exercise], name: str) -> Exercise | None:
    wanted_name = normalize_exercise_name(name).lower()
    for exercise in exercises:
        if exercise.name.lower() == wanted_name:
            return exercise
    return None


def next_workout_id(workouts: list[Workout]) -> int:
    if not workouts:
        return 1
    return workouts[-1].workout_id + 1


def current_workout(workouts: list[Workout]) -> Workout | None:
    if not workouts:
        return None
    return workouts[-1]


def find_workout(workouts: list[Workout], workout_id: int) -> Workout | None:
    for workout in workouts:
        if workout.workout_id == workout_id:
            return workout
    return None


def summarize_exercise(
    exercise: Exercise, workout_sets: list[WorkoutSet], workout_id: int
) -> ExerciseSummary:
    total_sets = 0
    total_reps = 0
    total_volume = 0.0

    for workout_set in workout_sets:
        if workout_set.workout_id == workout_id and workout_set.exercise_name == exercise.name:
            total_sets += 1
            total_reps += workout_set.reps
            total_volume += workout_set.reps * workout_set.weight

    return ExerciseSummary(
        name=exercise.name,
        muscle_group=exercise.muscle_group,
        total_sets=total_sets,
        total_reps=total_reps,
        total_volume=total_volume,
    )

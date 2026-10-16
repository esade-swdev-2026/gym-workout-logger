"""Read and write the workout data in CSV files."""

import csv
from pathlib import Path

from gym_workout_logger.workout import (
    Exercise,
    Workout,
    WorkoutSet,
    is_blank,
    is_valid_reps,
    is_valid_weight,
)

EXERCISES_HEADER = ["name", "muscle_group"]
WORKOUTS_HEADER = ["workout_id"]
WORKOUT_SETS_HEADER = ["workout_id", "exercise_name", "reps", "weight"]


def read_rows(path: Path, header: list[str]) -> list[list[str]]:
    """Return the rows of a CSV file without its header, or [] if the file does not exist."""
    if not path.exists():
        return []

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            if next(reader, None) != header:
                raise ValueError(f"{path.name} does not have the expected header.")
            rows = list(reader)
        except csv.Error as error:
            # csv.Error is not a ValueError, so the command would show a traceback.
            raise ValueError(f"{path.name} is damaged: {error}") from error

    for row in rows:
        if len(row) != len(header):
            raise ValueError(f"{path.name} has a row with the wrong number of values.")
    return rows


def append_row(path: Path, header: list[str], row: list[str | int | float]) -> None:
    """Add one row to a CSV file, writing the header first if the file is new."""
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if is_new:
            writer.writerow(header)
        writer.writerow(row)


def read_exercises(path: Path) -> list[Exercise]:
    exercises = []
    for name, muscle_group in read_rows(path, EXERCISES_HEADER):
        if is_blank(name) or is_blank(muscle_group):
            raise ValueError(f"{path.name} has an exercise with an empty name or muscle group.")
        exercises.append(Exercise(name=name, muscle_group=muscle_group))
    return exercises


def save_exercise(path: Path, exercise: Exercise) -> None:
    append_row(path, EXERCISES_HEADER, [exercise.name, exercise.muscle_group])


def read_workouts(path: Path) -> list[Workout]:
    workouts = []
    for row in read_rows(path, WORKOUTS_HEADER):
        workout_id = int(row[0])
        if workout_id <= 0:
            raise ValueError(f"{path.name} has a workout number that is not positive.")
        workouts.append(Workout(workout_id))
    return workouts


def save_workout(path: Path, workout: Workout) -> None:
    append_row(path, WORKOUTS_HEADER, [workout.workout_id])


def read_workout_sets(path: Path) -> list[WorkoutSet]:
    workout_sets = []
    for workout_id, exercise_name, reps, weight in read_rows(path, WORKOUT_SETS_HEADER):
        workout_set = WorkoutSet(
            exercise_name=exercise_name,
            reps=int(reps),
            weight=float(weight),
            workout_id=int(workout_id),
        )
        if not is_valid_reps(workout_set.reps) or not is_valid_weight(workout_set.weight):
            raise ValueError(f"{path.name} has a set with invalid reps or weight.")
        workout_sets.append(workout_set)
    return workout_sets


def save_workout_set(path: Path, workout_set: WorkoutSet) -> None:
    append_row(
        path,
        WORKOUT_SETS_HEADER,
        [workout_set.workout_id, workout_set.exercise_name, workout_set.reps, workout_set.weight],
    )

"""Read and write the workout data in CSV files."""

import csv
from pathlib import Path

from gym_workout_logger.workout import (
    Exercise,
    Workout,
    WorkoutSet,
    is_valid_exercise_name,
    is_valid_muscle_group,
    is_valid_reps,
    is_valid_weight,
)


def read_exercises(path: Path) -> list[Exercise]:
    if not path.exists():
        return []

    exercises = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        if next(reader, None) != ["name", "muscle_group"]:
            raise ValueError("Invalid exercises.csv header.")
        for row in reader:
            if (
                len(row) != 2
                or not is_valid_exercise_name(row[0])
                or not is_valid_muscle_group(row[1])
            ):
                raise ValueError("Invalid row in exercises.csv.")
            exercises.append(Exercise(name=row[0], muscle_group=row[1]))
    return exercises


def save_exercise(path: Path, exercise: Exercise) -> None:
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if needs_header:
            writer.writerow(["name", "muscle_group"])
        writer.writerow([exercise.name, exercise.muscle_group])


def read_workouts(path: Path) -> list[Workout]:
    if not path.exists():
        return []

    workouts = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        if next(reader, None) != ["workout_id"]:
            raise ValueError("Invalid workouts.csv header.")
        for row in reader:
            if len(row) != 1:
                raise ValueError("Invalid row in workouts.csv.")
            workout_id = int(row[0])
            if workout_id <= 0:
                raise ValueError("Invalid workout number in workouts.csv.")
            workouts.append(Workout(workout_id))
    return workouts


def save_workout(path: Path, workout: Workout) -> None:
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if needs_header:
            writer.writerow(["workout_id"])
        writer.writerow([workout.workout_id])


def read_workout_sets(path: Path) -> list[WorkoutSet]:
    if not path.exists():
        return []

    workout_sets = []
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        if next(reader, None) != ["workout_id", "exercise_name", "reps", "weight"]:
            raise ValueError("Invalid workout_sets.csv header (old format or damaged file).")
        for row in reader:
            if len(row) != 4:
                raise ValueError("Invalid row in workout_sets.csv.")
            workout_id = int(row[0])
            reps = int(row[2])
            weight = float(row[3])
            if (
                workout_id <= 0
                or not is_valid_exercise_name(row[1])
                or not is_valid_reps(reps)
                or not is_valid_weight(weight)
            ):
                raise ValueError("Invalid values in workout_sets.csv.")
            workout_sets.append(
                WorkoutSet(exercise_name=row[1], reps=reps, weight=weight, workout_id=workout_id)
            )
    return workout_sets


def save_workout_set(path: Path, workout_set: WorkoutSet) -> None:
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if needs_header:
            writer.writerow(["workout_id", "exercise_name", "reps", "weight"])
        writer.writerow(
            [
                workout_set.workout_id,
                workout_set.exercise_name,
                workout_set.reps,
                workout_set.weight,
            ]
        )

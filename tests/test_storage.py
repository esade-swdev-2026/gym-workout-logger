from pathlib import Path

from gym_workout_logger.storage import (
    read_exercises,
    read_workout_sets,
    read_workouts,
    save_exercise,
    save_workout,
    save_workout_set,
)
from gym_workout_logger.workout import Exercise, Workout, WorkoutSet


def test_missing_files_give_empty_lists(tmp_path: Path) -> None:
    assert read_exercises(tmp_path / "exercises.csv") == []
    assert read_workouts(tmp_path / "workouts.csv") == []
    assert read_workout_sets(tmp_path / "workout_sets.csv") == []


def test_saved_exercises_can_be_read_back(tmp_path: Path) -> None:
    csv_file = tmp_path / "exercises.csv"
    save_exercise(csv_file, Exercise("Squat", "legs"))

    assert read_exercises(csv_file) == [Exercise("Squat", "legs")]


def test_saved_workouts_and_sets_can_be_read_back(tmp_path: Path) -> None:
    workouts_file = tmp_path / "workouts.csv"
    sets_file = tmp_path / "workout_sets.csv"

    save_workout(workouts_file, Workout(1))
    save_workout_set(sets_file, WorkoutSet("Squat", 8, 62.5, 1))

    assert read_workouts(workouts_file) == [Workout(1)]
    assert read_workout_sets(sets_file) == [WorkoutSet("Squat", 8, 62.5, 1)]

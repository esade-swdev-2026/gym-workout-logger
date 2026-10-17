from pathlib import Path

import pytest

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
    save_exercise(csv_file, Exercise("Bench Press, incline", "chest"))

    result = read_exercises(csv_file)

    assert result == [Exercise("Squat", "legs"), Exercise("Bench Press, incline", "chest")]


def test_saved_workouts_and_sets_can_be_read_back(tmp_path: Path) -> None:
    workouts_file = tmp_path / "workouts.csv"
    sets_file = tmp_path / "workout_sets.csv"
    save_workout(workouts_file, Workout(1))
    save_workout_set(sets_file, WorkoutSet("Squat", 8, 62.5, 1))

    assert read_workouts(workouts_file) == [Workout(1)]
    assert read_workout_sets(sets_file) == [WorkoutSet("Squat", 8, 62.5, 1)]


def test_file_with_wrong_header_is_rejected(tmp_path: Path) -> None:
    csv_file = tmp_path / "workout_sets.csv"
    csv_file.write_text("exercise_name,reps,weight\nSquat,10,50\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected header"):
        read_workout_sets(csv_file)


def test_row_with_missing_values_is_rejected(tmp_path: Path) -> None:
    csv_file = tmp_path / "exercises.csv"
    csv_file.write_text("name,muscle_group\nSquat\n", encoding="utf-8")

    with pytest.raises(ValueError, match="wrong number of values"):
        read_exercises(csv_file)


def test_row_with_text_instead_of_number_is_rejected(tmp_path: Path) -> None:
    csv_file = tmp_path / "workout_sets.csv"
    csv_file.write_text("workout_id,exercise_name,reps,weight\n1,Squat,ten,50\n", encoding="utf-8")

    with pytest.raises(ValueError):
        read_workout_sets(csv_file)


@pytest.mark.parametrize("saved_set", ["1,Squat,-5,50", "1,Squat,0,50", "1,Squat,10,inf"])
def test_set_with_impossible_values_is_rejected(tmp_path: Path, saved_set: str) -> None:
    csv_file = tmp_path / "workout_sets.csv"
    csv_file.write_text(f"workout_id,exercise_name,reps,weight\n{saved_set}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid reps or weight"):
        read_workout_sets(csv_file)


def test_workout_number_that_is_not_positive_is_rejected(tmp_path: Path) -> None:
    csv_file = tmp_path / "workouts.csv"
    csv_file.write_text("workout_id\n-4\n", encoding="utf-8")

    with pytest.raises(ValueError, match="not positive"):
        read_workouts(csv_file)


def test_exercise_with_an_empty_name_is_rejected(tmp_path: Path) -> None:
    csv_file = tmp_path / "exercises.csv"
    csv_file.write_text("name,muscle_group\n   ,legs\n", encoding="utf-8")

    with pytest.raises(ValueError, match="empty name"):
        read_exercises(csv_file)


def test_damaged_file_raises_value_error_not_csv_error(tmp_path: Path) -> None:
    # A field over csv's size limit raises csv.Error, which the commands do not catch.
    csv_file = tmp_path / "exercises.csv"
    csv_file.write_text("name,muscle_group\n" + "A" * 200_000 + ",legs\n", encoding="utf-8")

    with pytest.raises(ValueError, match="damaged"):
        read_exercises(csv_file)

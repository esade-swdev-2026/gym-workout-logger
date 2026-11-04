from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app
from gym_workout_logger.delete_set import remove_workout_set
from gym_workout_logger.storage import (
    read_workout_sets,
    write_workout_sets,
    write_workouts,
)
from gym_workout_logger.workout import Workout, WorkoutSet


@pytest.fixture
def workout_sets() -> list[WorkoutSet]:
    return [
        WorkoutSet("Squat", 10, 50.0, 1),
        WorkoutSet("Bench Press", 8, 40.0, 2),
        WorkoutSet("Squat", 10, 50.0, 1),
    ]


def test_remove_set_keeps_sets_from_other_workouts() -> None:
    workout_sets = [
        WorkoutSet("Squat", 10, 50.0, 1),
        WorkoutSet("Bench Press", 8, 40.0, 2),
    ]

    result = remove_workout_set(workout_sets, workout_id=1, set_number=1)

    assert result == [WorkoutSet("Bench Press", 8, 40.0, 2)]


def test_remove_second_set_keeps_duplicate_and_original_list(
    workout_sets: list[WorkoutSet],
) -> None:
    original_sets = workout_sets.copy()

    result = remove_workout_set(workout_sets, 1, 2)

    assert result == original_sets[:2]
    assert workout_sets == original_sets


@pytest.mark.parametrize(
    ("workout_id", "set_number"),
    [(1, 0), (1, -1), (1, 3), (9, 1)],
)
def test_remove_missing_set_returns_none(
    workout_sets: list[WorkoutSet], workout_id: int, set_number: int
) -> None:
    assert remove_workout_set(workout_sets, workout_id, set_number) is None


def test_remove_from_empty_list_returns_none() -> None:
    assert remove_workout_set([], 1, 1) is None


def test_delete_command_saves_changes_and_rejects_missing_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    workout_sets: list[WorkoutSet],
) -> None:
    monkeypatch.chdir(tmp_path)
    write_workouts(Path("workouts.csv"), [Workout(1), Workout(2)])
    sets_file = Path("workout_sets.csv")
    write_workout_sets(sets_file, workout_sets)
    runner = CliRunner()

    result = runner.invoke(app, ["delete-set", "--workout-id", "1", "--set-number", "2"])

    assert result.exit_code == 0
    assert "Deleted set 2 from workout 1." in result.output
    assert read_workout_sets(sets_file) == workout_sets[:2]

    saved_content = sets_file.read_text()

    result = runner.invoke(app, ["delete-set", "--workout-id", "1", "--set-number", "8"])

    assert result.exit_code == 1
    assert "Set not found" in result.output
    assert sets_file.read_text() == saved_content

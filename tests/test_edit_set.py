from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app
from gym_workout_logger.edit_set import replace_workout_set
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


def test_edit_second_set_keeps_duplicate_and_original_list(
    workout_sets: list[WorkoutSet],
) -> None:
    original_sets = workout_sets.copy()

    result = replace_workout_set(workout_sets, 1, 2, 8, 55.0)

    assert result == original_sets[:2] + [WorkoutSet("Squat", 8, 55.0, 1)]
    assert workout_sets == original_sets


@pytest.mark.parametrize(
    ("workout_id", "set_number"),
    [(1, 3), (9, 1)],
)
def test_edit_missing_set_returns_none(
    workout_sets: list[WorkoutSet], workout_id: int, set_number: int
) -> None:
    assert replace_workout_set(workout_sets, workout_id, set_number, 8, 55.0) is None


@pytest.mark.parametrize(
    ("reps", "weight"),
    [
        (0, 50.0),
        (-1, 50.0),
        (8, -1.0),
        (8, float("inf")),
        (8, float("nan")),
    ],
)
def test_edit_rejects_invalid_values(
    workout_sets: list[WorkoutSet], reps: int, weight: float
) -> None:
    with pytest.raises(ValueError):
        replace_workout_set(workout_sets, 1, 1, reps, weight)


@pytest.mark.parametrize("set_number", [0, -1])
def test_edit_rejects_invalid_set_number(workout_sets: list[WorkoutSet], set_number: int) -> None:
    with pytest.raises(ValueError, match="Set number must be positive"):
        replace_workout_set(workout_sets, 1, set_number, 8, 55.0)


def test_edit_accepts_zero_weight(workout_sets: list[WorkoutSet]) -> None:
    result = replace_workout_set(workout_sets, 1, 1, 12, 0.0)

    assert result == [WorkoutSet("Squat", 12, 0.0, 1)] + workout_sets[1:]


def test_edit_empty_list_returns_none() -> None:
    assert replace_workout_set([], 1, 1, 8, 55.0) is None


def test_edit_command_saves_changes_and_rejects_invalid_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    workout_sets: list[WorkoutSet],
) -> None:
    monkeypatch.chdir(tmp_path)
    write_workouts(Path("workouts.csv"), [Workout(1), Workout(2)])
    sets_file = Path("workout_sets.csv")
    write_workout_sets(sets_file, workout_sets)
    runner = CliRunner()

    arguments = [
        "edit-set",
        "--workout-id",
        "1",
        "--set-number",
        "2",
        "--reps",
        "8",
        "--weight",
    ]

    result = runner.invoke(app, arguments + ["55"])

    assert result.exit_code == 0
    assert "Updated set 2 in workout 1." in result.output
    assert read_workout_sets(sets_file) == (workout_sets[:2] + [WorkoutSet("Squat", 8, 55.0, 1)])

    saved_content = sets_file.read_text()

    result = runner.invoke(app, arguments + ["-1"])

    assert result.exit_code == 1
    assert "weight must be finite and non-negative" in result.output
    assert sets_file.read_text() == saved_content

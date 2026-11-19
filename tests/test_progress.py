from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app
from gym_workout_logger.progress import max_weight_by_workout
from gym_workout_logger.workout import WorkoutSet


def test_max_weight_by_workout_groups_and_sorts() -> None:
    sets = [
        WorkoutSet("Squat", 10, 50.0, 2),
        WorkoutSet("Bench", 8, 80.0, 1),
        WorkoutSet("Squat", 5, 60.0, 2),
        WorkoutSet("Squat", 8, 40.0, 1),
    ]

    assert max_weight_by_workout(sets, "sQUat") == [(1, 40.0), (2, 60.0)]
    assert max_weight_by_workout([], "Squat") == []


def test_exercise_progress_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["add-exercise", "Squat"]).exit_code == 0
    assert runner.invoke(app, ["start-workout"]).exit_code == 0
    assert runner.invoke(app, ["log-set", "Squat", "10", "50"]).exit_code == 0

    result = runner.invoke(app, ["exercise-progress", "sQUat"])

    assert result.exit_code == 0
    assert "Workout 1 | Max weight: 50 kg" in result.output
    assert "Highest recorded weight: 50 kg" in result.output


def test_exercise_progress_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["exercise-progress", "Unknown"])

    assert result.exit_code == 1
    assert "Exercise not found" in result.output


def test_exercise_progress_no_sets_yet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["add-exercise", "Squat"]).exit_code == 0

    result = runner.invoke(app, ["exercise-progress", "Squat"])

    assert result.exit_code == 0
    assert "No sets logged for this exercise yet." in result.output

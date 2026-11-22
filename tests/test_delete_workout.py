from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app
from gym_workout_logger.delete_workout import rows_without_workout

runner = CliRunner()


# Unit tests for rows_without_workout()


def test_rows_without_workout_removes_matching_rows() -> None:
    rows = [
        ["1", "Bench Press", "3", "10"],
        ["2", "Squat", "4", "8"],
        ["1", "Deadlift", "3", "5"],
    ]

    result = rows_without_workout(rows, 1)

    assert result == [
        ["2", "Squat", "4", "8"],
    ]


def test_rows_without_workout_keeps_all_rows_when_no_match() -> None:
    rows = [
        ["1", "Bench Press", "3", "10"],
        ["2", "Squat", "4", "8"],
    ]

    result = rows_without_workout(rows, 3)

    assert result == rows


def test_rows_without_workout_returns_empty_when_all_match() -> None:
    rows = [
        ["1", "Bench Press", "3", "10"],
        ["1", "Squat", "4", "8"],
    ]

    result = rows_without_workout(rows, 1)

    assert result == []


def test_delete_workout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    runner.invoke(app, ["start-workout"])
    runner.invoke(app, ["start-workout"])

    result = runner.invoke(app, ["delete-workout", "--workout-id", "1"])

    assert result.exit_code == 0
    assert "Deleted workout 1" in result.output

    result = runner.invoke(app, ["summary", "--workout-id", "1"])
    assert result.exit_code == 1

    result = runner.invoke(app, ["summary", "--workout-id", "2"])
    assert result.exit_code == 0


def test_delete_nonexistent_workout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["delete-workout", "--workout-id", "99"])

    assert result.exit_code == 1
    assert "Workout not found" in result.output

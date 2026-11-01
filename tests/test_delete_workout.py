from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app

runner = CliRunner()


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

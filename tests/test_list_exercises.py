from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app


def test_list_exercises_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["list-exercises"])

    assert result.exit_code == 0
    assert "No exercises saved yet." in result.output


def test_list_exercises_shows_saved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    added = runner.invoke(app, ["add-exercise", "Squat", "--muscle-group", "legs"])
    assert added.exit_code == 0

    result = runner.invoke(app, ["list-exercises"])

    assert result.exit_code == 0
    assert "Squat | Muscle group: legs" in result.output

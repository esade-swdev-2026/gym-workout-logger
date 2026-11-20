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


def test_list_exercises_invalid_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("exercises.csv").write_text("name,muscle_group\n,legs\n", encoding="utf-8")

    result = CliRunner().invoke(app, ["list-exercises"])

    assert result.exit_code == 1
    assert "Could not list exercises:" in result.output

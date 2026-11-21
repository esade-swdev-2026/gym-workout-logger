from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app
from gym_workout_logger.storage import read_rows


def test_assign_and_replace_workout_date(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["start-workout"]).exit_code == 0

    for value in ("2026-11-19", "2026-11-20"):
        result = runner.invoke(
            app,
            ["set-workout-date", "--workout-id", "1", "--date", value],
        )
        assert result.exit_code == 0

    assert read_rows(Path("workout_dates.csv"), ["workout_id", "date"]) == [["1", "2026-11-20"]]

    display = runner.invoke(app, ["list-workout-dates"])
    assert display.exit_code == 0
    assert "Workout 1 | Date: 2026-11-20" in display.output


def test_invalid_date_does_not_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["start-workout"]).exit_code == 0

    result = runner.invoke(
        app,
        ["set-workout-date", "--workout-id", "1", "--date", "2026-99-99"],
    )

    assert result.exit_code == 1
    assert not Path("workout_dates.csv").exists()


def test_delete_workout_cleans_up_date(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["start-workout"]).exit_code == 0

    assert (
        runner.invoke(
            app,
            ["set-workout-date", "--workout-id", "1", "--date", "2026-11-19"],
        ).exit_code
        == 0
    )

    assert runner.invoke(app, ["delete-workout", "--workout-id", "1"]).exit_code == 0

    assert read_rows(Path("workout_dates.csv"), ["workout_id", "date"]) == []


def test_delete_workout_with_invalid_date_file_preserves_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    assert runner.invoke(app, ["start-workout"]).exit_code == 0

    assert (
        runner.invoke(app, ["add-exercise", "Bench Press", "--muscle-group", "chest"]).exit_code
        == 0
    )
    assert runner.invoke(app, ["log-set", "Bench Press", "10", "60"]).exit_code == 0

    workouts_before = Path("workouts.csv").read_text(encoding="utf-8")
    sets_before = Path("workout_sets.csv").read_text(encoding="utf-8")

    Path("workout_dates.csv").write_text("workout_id,date\nbad-id,2026-11-19\n", encoding="utf-8")

    result = runner.invoke(app, ["delete-workout", "--workout-id", "1"])

    assert result.exit_code == 1
    assert Path("workouts.csv").read_text(encoding="utf-8") == workouts_before
    assert Path("workout_sets.csv").read_text(encoding="utf-8") == sets_before


def test_list_workout_dates_with_invalid_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    Path("workout_dates.csv").write_text("workout_id,date\nbad-id,2026-11-19\n", encoding="utf-8")

    result = runner.invoke(app, ["list-workout-dates"])

    assert result.exit_code == 1
    assert "Could not list workout dates" in result.output

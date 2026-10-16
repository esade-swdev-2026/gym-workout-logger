from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app

runner = CliRunner()


def test_workout_commands_and_saved_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["add-exercise", "Squat", "--muscle-group", "legs"])
    assert result.exit_code == 0
    assert "Exercise: Squat | Muscle group: legs" in result.output

    result = runner.invoke(app, ["add-exercise", "Bench Press", "--muscle-group", "chest"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["log-set", "Squat", "10", "50"])
    assert result.exit_code == 1
    assert "Run start-workout first" in result.output

    result = runner.invoke(app, ["start-workout"])
    assert result.exit_code == 0
    assert "Started workout 1" in result.output

    result = runner.invoke(app, ["log-set", "sQUat", "10", "50"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["log-set", "Squat", "8", "55"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["log-set", "Bench Press", "6", "40"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "Workout 1" in result.output
    assert "Squat" in result.output
    assert "Sets: 2 | Reps: 18 | Volume: 940 kg" in result.output
    assert "Bench Press" in result.output

    result = runner.invoke(app, ["start-workout"])
    assert result.exit_code == 0
    assert "Started workout 2" in result.output

    result = runner.invoke(app, ["summary"])
    assert "Workout 2" in result.output
    assert "No sets logged" in result.output
    assert "940 kg" not in result.output

    result = runner.invoke(app, ["log-set", "Squat", "5", "80"])
    assert result.exit_code == 0
    result = runner.invoke(app, ["summary"])
    assert "Sets: 1 | Reps: 5 | Volume: 400 kg" in result.output
    assert "940 kg" not in result.output

    result = runner.invoke(app, ["summary", "--workout-id", "1"])
    assert result.exit_code == 0
    assert "Workout 1" in result.output
    assert "Sets: 2 | Reps: 18 | Volume: 940 kg" in result.output
    assert (tmp_path / "workouts.csv").exists()
    assert (tmp_path / "workout_sets.csv").exists()


def test_invalid_inputs_and_damaged_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["add-exercise", "  "])
    assert result.exit_code == 1
    assert "Exercise name cannot be empty" in result.output

    assert runner.invoke(app, ["add-exercise", "Squat"]).exit_code == 0
    result = runner.invoke(app, ["add-exercise", "  SQUAT  "])
    assert result.exit_code == 1
    assert "already been added" in result.output

    assert runner.invoke(app, ["start-workout"]).exit_code == 0

    result = runner.invoke(app, ["log-set", "Unknown", "10", "30"])
    assert result.exit_code == 1
    assert "Exercise not found" in result.output

    result = runner.invoke(app, ["log-set", "Squat", "0", "50"])
    assert result.exit_code == 1
    assert "Reps must be greater than zero" in result.output

    for bad_weight in ["-2", "nan", "inf", "1e309"]:
        result = runner.invoke(app, ["log-set", "Squat", "10", bad_weight])
        assert result.exit_code != 0
        assert "Traceback" not in result.output

    assert not (tmp_path / "workout_sets.csv").exists()

    result = runner.invoke(app, ["summary", "--workout-id", "99"])
    assert result.exit_code == 1
    assert "Workout not found" in result.output

    (tmp_path / "workout_sets.csv").write_text(
        "workout_id,exercise_name,reps,weight\n1,Squat,10,inf\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 1
    assert "Invalid values in workout_sets.csv" in result.output
    assert "Traceback" not in result.output

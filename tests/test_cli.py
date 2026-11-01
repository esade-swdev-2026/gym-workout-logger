from pathlib import Path

import pytest
from typer.testing import CliRunner

from gym_workout_logger.cli import app

runner = CliRunner()


@pytest.fixture
def in_empty_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    # The CSV files are created in the current folder, so each test gets its own empty one.
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_log_sets_and_show_summary(in_empty_folder: Path) -> None:
    runner.invoke(app, ["add-exercise", "Squat", "--muscle-group", "legs"])
    runner.invoke(app, ["start-workout"])
    runner.invoke(app, ["log-set", "sQUat", "10", "50"])

    result = runner.invoke(app, ["log-set", "Squat", "8", "55"])
    assert result.exit_code == 0
    assert "Workout 1 | Squat | Reps: 8 | Weight: 55 kg" in result.stdout

    result = runner.invoke(app, ["summary"])
    assert result.exit_code == 0
    assert "Squat | Muscle group: legs | Sets: 2 | Reps: 18 | Volume: 940 kg" in result.stdout


def test_new_workout_starts_empty_and_old_one_stays_saved(in_empty_folder: Path) -> None:
    runner.invoke(app, ["add-exercise", "Squat"])
    runner.invoke(app, ["start-workout"])
    runner.invoke(app, ["log-set", "Squat", "10", "50"])

    result = runner.invoke(app, ["start-workout"])
    assert "Started workout 2" in result.stdout

    result = runner.invoke(app, ["summary"])
    assert "Workout 2" in result.stdout
    assert "No sets logged" in result.stdout

    result = runner.invoke(app, ["summary", "--workout-id", "1"])
    assert result.exit_code == 0
    assert "Sets: 1 | Reps: 10 | Volume: 500 kg" in result.stdout


def test_log_set_before_starting_a_workout_fails(in_empty_folder: Path) -> None:
    runner.invoke(app, ["add-exercise", "Squat"])

    result = runner.invoke(app, ["log-set", "Squat", "10", "50"])

    assert result.exit_code == 1
    assert "Run start-workout first" in result.stderr


def test_unknown_exercise_fails(in_empty_folder: Path) -> None:
    runner.invoke(app, ["start-workout"])

    result = runner.invoke(app, ["log-set", "Unknown", "10", "30"])

    assert result.exit_code == 1
    assert "Exercise not found" in result.stderr


def test_empty_and_duplicate_exercise_names_fail(in_empty_folder: Path) -> None:
    result = runner.invoke(app, ["add-exercise", "  "])
    assert result.exit_code == 1
    assert "Exercise name cannot be empty" in result.stderr

    runner.invoke(app, ["add-exercise", "Squat"])
    result = runner.invoke(app, ["add-exercise", "  SQUAT  "])
    assert result.exit_code == 1
    assert "already been added" in result.stderr


@pytest.mark.parametrize(
    ("reps", "weight"), [("0", "50"), ("10", "nan"), ("10", "inf"), ("10", "1e309")]
)
def test_invalid_reps_or_weight_fail_without_saving(
    in_empty_folder: Path, reps: str, weight: str
) -> None:
    runner.invoke(app, ["add-exercise", "Squat"])
    runner.invoke(app, ["start-workout"])

    result = runner.invoke(app, ["log-set", "Squat", reps, weight])

    assert result.exit_code == 1
    assert not (in_empty_folder / "workout_sets.csv").exists()


def test_unknown_workout_number_fails(in_empty_folder: Path) -> None:
    runner.invoke(app, ["start-workout"])

    result = runner.invoke(app, ["summary", "--workout-id", "99"])

    assert result.exit_code == 1
    assert "Workout not found" in result.stderr


def test_damaged_file_gives_a_message_not_a_traceback(in_empty_folder: Path) -> None:
    runner.invoke(app, ["start-workout"])
    (in_empty_folder / "workout_sets.csv").write_text(
        "workout_id,exercise_name,reps,weight\n1,Squat,ten,50\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["summary"])

    assert result.exit_code == 1
    assert "Could not read saved data" in result.stderr


def test_list_workouts_empty(in_empty_folder: Path) -> None:
    result = runner.invoke(app, ["list-workouts"])
    assert result.exit_code == 0
    assert "No workouts saved yet." in result.stdout


def test_list_workouts_shows_saved_workouts(in_empty_folder: Path) -> None:
    runner.invoke(app, ["start-workout"])
    runner.invoke(app, ["start-workout"])
    result = runner.invoke(app, ["list-workouts"])
    assert result.exit_code == 0
    assert "Workout 1" in result.stdout
    assert "Workout 2" in result.stdout

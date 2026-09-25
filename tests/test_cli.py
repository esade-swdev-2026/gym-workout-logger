from typer.testing import CliRunner

from gym_workout_logger.cli import app

runner = CliRunner()


def test_add_exercise() -> None:
    result = runner.invoke(app, ["add-exercise", "Squat", "--muscle-group", "legs"])
    assert result.exit_code == 0
    assert "Exercise: Squat | Muscle group: legs" in result.output


def test_default_muscle_group() -> None:
    result = runner.invoke(app, ["add-exercise", "Squat"])
    assert result.exit_code == 0
    assert "Muscle group: full body" in result.output


def test_empty_name() -> None:
    result = runner.invoke(app, ["add-exercise", " "])
    assert result.exit_code == 1
    assert "Exercise name cannot be empty" in result.output

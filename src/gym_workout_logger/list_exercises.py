from pathlib import Path

import typer

from gym_workout_logger.storage import read_exercises


def list_exercises() -> None:
    """Show saved exercises and their muscle groups."""
    try:
        exercises = read_exercises(Path("exercises.csv"))
    except (OSError, ValueError) as error:
        typer.echo(f"Could not list exercises: {error}", err=True)
        raise typer.Exit(1) from None

    if not exercises:
        typer.echo("No exercises saved yet.")
        return

    for exercise in exercises:
        typer.echo(f"{exercise.name} | Muscle group: {exercise.muscle_group}")

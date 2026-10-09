import typer

from gym_workout_logger.workout import (
    create_exercise,
    is_valid_exercise_name,
    is_valid_muscle_group,
)

app = typer.Typer(help="Replace this with your project's command-line interface.")


@app.callback()
def main() -> None:
    """A terminal gym workout logger."""


@app.command()
def add_exercise(
    name: str,
    muscle_group: str = typer.Option("full body", "--muscle-group"),
) -> None:
    if not is_valid_exercise_name(name):
        typer.echo("Exercise name cannot be empty.", err=True)
        raise typer.Exit(code=1)

    if not is_valid_muscle_group(muscle_group):
        typer.echo("Muscle group cannot be empty.", err=True)
        raise typer.Exit(code=1)

    exercise = create_exercise(name, muscle_group)

    typer.echo(f"Exercise: {exercise.name} | Muscle group: {exercise.muscle_group}")


if __name__ == "__main__":
    app()

from pathlib import Path

import typer

from gym_workout_logger.storage import read_exercises, read_workout_sets
from gym_workout_logger.workout import WorkoutSet, find_exercise


def max_weight_by_workout(
    workout_sets: list[WorkoutSet], exercise_name: str
) -> list[tuple[int, float]]:
    weights: dict[int, float] = {}

    for item in workout_sets:
        if item.exercise_name.casefold() != exercise_name.casefold():
            continue

        weights[item.workout_id] = max(weights.get(item.workout_id, 0.0), item.weight)

    return sorted(weights.items())


def exercise_progress(name: str) -> None:
    """Show the heaviest set of one exercise in each workout."""
    try:
        exercises = read_exercises(Path("exercises.csv"))
        workout_sets = read_workout_sets(Path("workout_sets.csv"))
    except (OSError, ValueError) as error:
        typer.echo(f"Could not read saved data: {error}", err=True)
        raise typer.Exit(1) from None

    exercise = find_exercise(exercises, name)
    if exercise is None:
        typer.echo("Exercise not found.", err=True)
        raise typer.Exit(1)

    progress = max_weight_by_workout(workout_sets, exercise.name)
    typer.echo(f"Exercise progress: {exercise.name}")

    if not progress:
        typer.echo("No sets logged for this exercise yet.")
        return

    for workout_id, weight in progress:
        typer.echo(f"Workout {workout_id} | Max weight: {weight:g} kg")

    typer.echo(f"Highest recorded weight: {max(w for _, w in progress):g} kg")

from pathlib import Path

import typer

from gym_workout_logger.storage import (
    read_workout_sets,
    read_workouts,
    write_workout_sets,
)
from gym_workout_logger.workout import WorkoutSet, find_workout


def remove_workout_set(
    workout_sets: list[WorkoutSet], workout_id: int, set_number: int
) -> list[WorkoutSet] | None:
    if set_number < 1:
        return None
    current_number = 0
    for index, workout_set in enumerate(workout_sets):
        if workout_set.workout_id == workout_id:
            current_number += 1
            if current_number == set_number:
                return workout_sets[:index] + workout_sets[index + 1 :]
    return None


def delete_set(
    workout_id: int = typer.Option(..., "--workout-id"),
    set_number: int = typer.Option(..., "--set-number"),
) -> None:
    try:
        workouts = read_workouts(Path("workouts.csv"))
        if find_workout(workouts, workout_id) is None:
            typer.echo("Workout not found.", err=True)
            raise typer.Exit(1)

        workout_sets = read_workout_sets(Path("workout_sets.csv"))
        updated_sets = remove_workout_set(workout_sets, workout_id, set_number)

        if updated_sets is None:
            typer.echo(
                "Set not found. Set numbers start at 1 within each workout.",
                err=True,
            )
            raise typer.Exit(1)

        write_workout_sets(Path("workout_sets.csv"), updated_sets)
    except (OSError, ValueError) as error:
        typer.echo(f"Could not delete set: {error}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Deleted set {set_number} from workout {workout_id}.")

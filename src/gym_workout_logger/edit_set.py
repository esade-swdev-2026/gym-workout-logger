from dataclasses import replace
from pathlib import Path

import typer

from gym_workout_logger.storage import (
    read_workout_sets,
    read_workouts,
    write_workout_sets,
)
from gym_workout_logger.workout import (
    WorkoutSet,
    find_workout,
    is_valid_reps,
    is_valid_weight,
)


def replace_workout_set(
    workout_sets: list[WorkoutSet],
    workout_id: int,
    set_number: int,
    reps: int,
    weight: float,
) -> list[WorkoutSet] | None:
    if set_number < 1:
        raise ValueError("Set number must be positive.")

    if not is_valid_reps(reps) or not is_valid_weight(weight):
        raise ValueError("Reps must be positive; weight must be finite and non-negative.")

    current_number = 0
    for index, workout_set in enumerate(workout_sets):
        if workout_set.workout_id == workout_id:
            current_number += 1
            if current_number == set_number:
                updated_sets = workout_sets.copy()
                updated_sets[index] = replace(workout_set, reps=reps, weight=weight)
                return updated_sets

    return None


def edit_set(
    workout_id: int = typer.Option(..., "--workout-id"),
    set_number: int = typer.Option(..., "--set-number"),
    reps: int = typer.Option(..., "--reps"),
    weight: float = typer.Option(..., "--weight"),
) -> None:
    try:
        workouts = read_workouts(Path("workouts.csv"))

        if find_workout(workouts, workout_id) is None:
            typer.echo("Workout not found.", err=True)
            raise typer.Exit(1)

        workout_sets = read_workout_sets(Path("workout_sets.csv"))

        updated_sets = replace_workout_set(workout_sets, workout_id, set_number, reps, weight)

        if updated_sets is None:
            typer.echo(
                "Set not found. Set numbers start at 1 within each workout.",
                err=True,
            )
            raise typer.Exit(1)

        write_workout_sets(Path("workout_sets.csv"), updated_sets)

    except typer.Exit:
        raise
    except (OSError, ValueError) as error:
        typer.echo(f"Could not edit set: {error}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Updated set {set_number} in workout {workout_id}.")

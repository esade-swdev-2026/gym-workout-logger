from pathlib import Path

import typer

from gym_workout_logger.delete_workout import delete_workout
from gym_workout_logger.storage import (
    read_exercises,
    read_workout_sets,
    read_workouts,
    save_exercise,
    save_workout,
    save_workout_set,
)
from gym_workout_logger.workout import (
    Workout,
    WorkoutSet,
    create_exercise,
    current_workout,
    find_exercise,
    find_workout,
    format_summary,
    is_blank,
    is_valid_reps,
    is_valid_weight,
    next_workout_id,
    summarize_workout,
)

EXERCISES_FILE = Path("exercises.csv")
WORKOUTS_FILE = Path("workouts.csv")
WORKOUT_SETS_FILE = Path("workout_sets.csv")

DEFAULT_MUSCLE_GROUP = "full body"

app = typer.Typer(help="Record gym exercises, sets, reps and weights.")
app.command("delete-workout")(delete_workout)


@app.callback()
def main() -> None:
    """A terminal gym workout logger."""


@app.command()
def add_exercise(
    name: str,
    muscle_group: str = typer.Option(DEFAULT_MUSCLE_GROUP, "--muscle-group"),
) -> None:
    """Save a new exercise to use in your workouts."""
    if is_blank(name):
        typer.echo("Exercise name cannot be empty.", err=True)
        raise typer.Exit(1)
    if is_blank(muscle_group):
        typer.echo("Muscle group cannot be empty.", err=True)
        raise typer.Exit(1)

    try:
        exercises = read_exercises(EXERCISES_FILE)
    except (OSError, ValueError) as error:
        typer.echo(f"Could not read saved data: {error}", err=True)
        raise typer.Exit(1) from None

    exercise = create_exercise(name, muscle_group)
    if find_exercise(exercises, exercise.name) is not None:
        typer.echo("This exercise has already been added.", err=True)
        raise typer.Exit(1)

    try:
        save_exercise(EXERCISES_FILE, exercise)
    except OSError as error:
        typer.echo(f"Could not save exercise: {error}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Exercise: {exercise.name} | Muscle group: {exercise.muscle_group}")


@app.command()
def start_workout() -> None:
    """Start another workout, keeping previous workouts saved."""
    try:
        workouts = read_workouts(WORKOUTS_FILE)
        workout = Workout(next_workout_id(workouts))
        save_workout(WORKOUTS_FILE, workout)
    except (OSError, ValueError) as error:
        typer.echo(f"Could not start workout: {error}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Started workout {workout.workout_id}.")


@app.command()
def log_set(name: str, reps: int, weight: float) -> None:
    """Log one set for the latest workout (weight in kg)."""
    if not is_valid_reps(reps):
        typer.echo("Reps must be greater than zero.", err=True)
        raise typer.Exit(1)
    if not is_valid_weight(weight):
        typer.echo("Weight must be a finite number and cannot be negative.", err=True)
        raise typer.Exit(1)

    try:
        workouts = read_workouts(WORKOUTS_FILE)
        exercises = read_exercises(EXERCISES_FILE)
    except (OSError, ValueError) as error:
        typer.echo(f"Could not read saved data: {error}", err=True)
        raise typer.Exit(1) from None

    workout = current_workout(workouts)
    if workout is None:
        typer.echo("No workout started. Run start-workout first.", err=True)
        raise typer.Exit(1)
    exercise = find_exercise(exercises, name)
    if exercise is None:
        typer.echo("Exercise not found. Add it before logging a set.", err=True)
        raise typer.Exit(1)

    workout_set = WorkoutSet(
        exercise_name=exercise.name, reps=reps, weight=weight, workout_id=workout.workout_id
    )
    try:
        save_workout_set(WORKOUT_SETS_FILE, workout_set)
    except OSError as error:
        typer.echo(f"Could not log set: {error}", err=True)
        raise typer.Exit(1) from None

    typer.echo(
        f"Workout {workout.workout_id} | {exercise.name} | Reps: {reps} | Weight: {weight:g} kg"
    )


@app.command()
def summary(workout_id: int | None = typer.Option(None, "--workout-id")) -> None:
    """Show the latest workout, or a previous workout by number."""
    try:
        workouts = read_workouts(WORKOUTS_FILE)
        exercises = read_exercises(EXERCISES_FILE)
        workout_sets = read_workout_sets(WORKOUT_SETS_FILE)
    except (OSError, ValueError) as error:
        typer.echo(f"Could not read saved data: {error}", err=True)
        raise typer.Exit(1) from None

    if workout_id is None:
        workout = current_workout(workouts)
    else:
        workout = find_workout(workouts, workout_id)
    if workout is None:
        typer.echo("Workout not found. Run start-workout first.", err=True)
        raise typer.Exit(1)

    summaries = summarize_workout(exercises, workout_sets, workout.workout_id)
    for line in format_summary(workout.workout_id, summaries):
        typer.echo(line)

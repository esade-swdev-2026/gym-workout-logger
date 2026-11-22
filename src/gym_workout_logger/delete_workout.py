import csv
from pathlib import Path

import typer

from gym_workout_logger.storage import read_rows, read_workout_sets, read_workouts
from gym_workout_logger.workout import find_workout
from gym_workout_logger.workout_dates import DATE_FILE, DATE_HEADER


def rows_without_workout(rows: list[list[str]], workout_id: int) -> list[list[str]]:
    return [row for row in rows if int(row[0]) != workout_id]


def remove_workout_rows(path: Path, workout_id: int) -> None:
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    remaining_rows = [rows[0], *rows_without_workout(rows[1:], workout_id)]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(remaining_rows)


def delete_workout(
    workout_id: int = typer.Option(..., "--workout-id"),
) -> None:
    """Delete a workout and all its logged sets."""
    workouts_file = Path("workouts.csv")
    sets_file = Path("workout_sets.csv")

    try:
        workouts = read_workouts(workouts_file)
        read_workout_sets(sets_file)

        if find_workout(workouts, workout_id) is None:
            typer.echo("Workout not found.", err=True)
            raise typer.Exit(code=1)

        date_rows = read_rows(DATE_FILE, DATE_HEADER)
        remaining_dates = rows_without_workout(date_rows, workout_id)

        remove_workout_rows(sets_file, workout_id)
        remove_workout_rows(workouts_file, workout_id)

        if len(remaining_dates) != len(date_rows):
            with DATE_FILE.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(DATE_HEADER)
                writer.writerows(remaining_dates)

    except (OSError, ValueError, IndexError) as error:
        typer.echo(f"Could not delete workout: {error}", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(f"Deleted workout {workout_id}.")

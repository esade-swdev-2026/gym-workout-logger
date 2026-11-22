import csv
from datetime import date
from pathlib import Path

import typer

from gym_workout_logger.storage import read_rows, read_workouts
from gym_workout_logger.workout import find_workout

DATE_FILE = Path("workout_dates.csv")
DATE_HEADER = ["workout_id", "date"]


def save_workout_date(path: Path, workout_id: int, date_text: str) -> None:
    rows = read_rows(path, DATE_HEADER)
    updated_rows = [row for row in rows if int(row[0]) != workout_id]
    updated_rows.append([str(workout_id), date_text])

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(DATE_HEADER)
        writer.writerows(updated_rows)


def set_workout_date(
    workout_id: int = typer.Option(..., "--workout-id"),
    date_text: str = typer.Option(..., "--date"),
) -> None:
    """Assign a date (YYYY-MM-DD) to a workout."""
    try:
        parsed = date.fromisoformat(date_text)
        if parsed.isoformat() != date_text:
            raise ValueError("Use YYYY-MM-DD.")

        workouts = read_workouts(Path("workouts.csv"))
        if find_workout(workouts, workout_id) is None:
            typer.echo("Workout not found.", err=True)
            raise typer.Exit(1)

        save_workout_date(DATE_FILE, workout_id, date_text)

    except (OSError, ValueError) as error:
        typer.echo(f"Could not save workout date: {error}", err=True)
        raise typer.Exit(1) from None

    typer.echo(f"Workout {workout_id} date: {date_text}.")


def list_workout_dates() -> None:
    """Show the dates assigned to workouts."""
    try:
        rows = read_rows(DATE_FILE, DATE_HEADER)
        rows.sort(key=lambda row: int(row[0]))

        if not rows:
            typer.echo("No workout dates saved yet.")
            return

        for workout_id, date_text in rows:
            typer.echo(f"Workout {workout_id} | Date: {date_text}")

    except (OSError, ValueError, IndexError) as error:
        typer.echo(f"Could not list workout dates: {error}", err=True)
        raise typer.Exit(1) from None

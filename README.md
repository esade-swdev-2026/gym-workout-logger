# Gym Workout Logger

Gym Workout Logger is a Python terminal program for recording gym exercises and workouts. You can add exercises, start a workout, log sets with reps and weight, and see a summary of that workout. Previous workouts are kept separately.

## Install

Needs [uv](https://docs.astral.sh/uv/) and Python 3.13. Clone the repository and install the dependencies:

```bash
git clone https://github.com/esade-swdev-2026/gym-workout-logger.git
cd gym-workout-logger
uv sync
```

`uv` uses `pyproject.toml` and `uv.lock` to set up the project environment.

## Run

Run these commands in order, from the project folder:

```bash
uv run gym-workout-logger --help
uv run gym-workout-logger add-exercise "Bench Press" --muscle-group chest
uv run gym-workout-logger add-exercise "Squat" --muscle-group legs
uv run gym-workout-logger start-workout
uv run gym-workout-logger log-set "Bench Press" 10 50
uv run gym-workout-logger log-set "bench press" 8 55
uv run gym-workout-logger log-set "Squat" 8 60
uv run gym-workout-logger summary
```

The summary shows the exercises completed in **Workout 1**, including sets, reps, and total volume (reps × weight, in kg):

```text
Workout 1
Exercise: Bench Press | Muscle group: chest | Sets: 2 | Reps: 18 | Volume: 940 kg
Exercise: Squat | Muscle group: legs | Sets: 1 | Reps: 8 | Volume: 480 kg
```

To train again, start another workout. This starts with no sets but keeps Workout 1 saved:

```bash
uv run gym-workout-logger start-workout
uv run gym-workout-logger log-set "Bench Press" 6 60
uv run gym-workout-logger summary
uv run gym-workout-logger summary --workout-id 1
```

`summary` always shows the latest workout. Use `--workout-id` to view an earlier one. Workout numbers start at 1 and increase by 1 each time you run `start-workout`.

An exercise must be added once before logging a set. If you leave out `--muscle-group`, it is saved as `full body`. Exercise names ignore differences in uppercase/lowercase and surrounding spaces. Sets need positive whole-number reps and a non-negative, finite weight. Use `0` kg for bodyweight exercises.

`uv run gym-workout-logger <command> --help` shows the arguments and options of each command. Invalid input prints a short message instead of a traceback, and the program exits with a non-zero code.

## Saved data

The program creates three CSV files in the folder where you run the commands:

- `exercises.csv` — exercises you have added
- `workouts.csv` — workout numbers
- `workout_sets.csv` — sets linked to a workout number and an exercise

They are ignored by Git. Your data stays there between runs, even after closing the terminal. To start again from nothing, delete the three files.

## Checks

Run the same checks as GitHub Actions:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

To format the code before checking, use `uv run ruff format .`.

## Project layout

```text
src/gym_workout_logger/
    cli.py       terminal commands, output and error messages
    workout.py   data classes, validation and calculations
    storage.py   CSV file reading and writing
    __main__.py  run the package with Python

tests/
    test_workout.py  the calculations, with plain data
    test_storage.py  reading and writing CSV files in a temporary folder
    test_cli.py      the commands, run with Typer's CliRunner
pyproject.toml  dependencies and configuration
uv.lock         locked dependency versions
```

The calculations in `workout.py` use plain Python data rather than files or printing, so they are straightforward to test. `cli.py` is the thin outer layer: it reads the files, calls those functions and prints the result.

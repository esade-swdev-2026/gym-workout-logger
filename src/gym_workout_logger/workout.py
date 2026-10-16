"""Workout data and calculations. No file reading or printing here."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Exercise:
    name: str
    muscle_group: str


@dataclass(frozen=True)
class Workout:
    workout_id: int


@dataclass(frozen=True)
class WorkoutSet:
    exercise_name: str
    reps: int
    weight: float
    workout_id: int


@dataclass(frozen=True)
class ExerciseSummary:
    name: str
    muscle_group: str
    total_sets: int
    total_reps: int
    total_volume: float


def is_blank(text: str) -> bool:
    return text.strip() == ""


def is_valid_reps(reps: int) -> bool:
    return reps > 0


def is_valid_weight(weight: float) -> bool:
    return isfinite(weight) and weight >= 0.0


def create_exercise(name: str, muscle_group: str) -> Exercise:
    return Exercise(name=name.strip(), muscle_group=muscle_group.strip())


def find_exercise(exercises: list[Exercise], name: str) -> Exercise | None:
    # Names are matched ignoring case and surrounding spaces, so "squat " finds "Squat".
    wanted_name = name.strip().lower()
    for exercise in exercises:
        if exercise.name.lower() == wanted_name:
            return exercise
    return None


def next_workout_id(workouts: list[Workout]) -> int:
    if not workouts:
        return 1
    return workouts[-1].workout_id + 1


def current_workout(workouts: list[Workout]) -> Workout | None:
    if not workouts:
        return None
    return workouts[-1]


def find_workout(workouts: list[Workout], workout_id: int) -> Workout | None:
    for workout in workouts:
        if workout.workout_id == workout_id:
            return workout
    return None


def summarize_exercise(
    exercise: Exercise, workout_sets: list[WorkoutSet], workout_id: int
) -> ExerciseSummary:
    total_sets = 0
    total_reps = 0
    total_volume = 0.0

    for workout_set in workout_sets:
        if workout_set.workout_id != workout_id or workout_set.exercise_name != exercise.name:
            continue
        total_sets += 1
        total_reps += workout_set.reps
        total_volume += workout_set.reps * workout_set.weight

    return ExerciseSummary(
        name=exercise.name,
        muscle_group=exercise.muscle_group,
        total_sets=total_sets,
        total_reps=total_reps,
        total_volume=total_volume,
    )


def summarize_workout(
    exercises: list[Exercise], workout_sets: list[WorkoutSet], workout_id: int
) -> list[ExerciseSummary]:
    summaries = []
    for exercise in exercises:
        summary = summarize_exercise(exercise, workout_sets, workout_id)
        if summary.total_sets > 0:
            summaries.append(summary)
    return summaries


def format_summary(workout_id: int, summaries: list[ExerciseSummary]) -> list[str]:
    lines = [f"Workout {workout_id}"]
    if not summaries:
        lines.append("No sets logged for this workout yet.")
    for summary in summaries:
        lines.append(
            f"Exercise: {summary.name} | Muscle group: {summary.muscle_group} | "
            f"Sets: {summary.total_sets} | Reps: {summary.total_reps} | "
            f"Volume: {summary.total_volume:g} kg"
        )
    return lines

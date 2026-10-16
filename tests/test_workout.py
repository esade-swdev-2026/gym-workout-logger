import pytest

from gym_workout_logger.workout import (
    ExerciseSummary,
    Workout,
    WorkoutSet,
    create_exercise,
    current_workout,
    find_exercise,
    find_workout,
    is_valid_exercise_name,
    is_valid_muscle_group,
    is_valid_reps,
    is_valid_weight,
    next_workout_id,
    normalize_exercise_name,
    normalize_muscle_group,
    summarize_exercise,
)


def test_exercise_name_removes_surrounding_whitespace() -> None:
    assert normalize_exercise_name("  Squat  ") == "Squat"


def test_exercise_muscle_group_removes_surrounding_whitespace() -> None:
    assert normalize_muscle_group("  Legs  ") == "Legs"


@pytest.mark.parametrize(
    ("name", "expected"),
    [("Squat", True), ("", False), ("   ", False)],
)
def test_exercise_name_validation(name: str, expected: bool) -> None:
    result = is_valid_exercise_name(name)
    assert result == expected


@pytest.mark.parametrize(
    ("muscle_group", "expected"),
    [("legs", True), ("", False), ("   ", False)],
)
def test_muscle_group_validation(muscle_group: str, expected: bool) -> None:
    result = is_valid_muscle_group(muscle_group)
    assert result == expected


def test_create_exercise_removes_surrounding_whitespace() -> None:
    result = create_exercise("  Squat  ", "  legs  ")
    assert result.name == "Squat"
    assert result.muscle_group == "legs"


def test_find_exercise_ignores_case_and_spaces() -> None:
    exercises = [create_exercise("Squat", "legs"), create_exercise("Bench Press", "chest")]
    result = find_exercise(exercises, "  squat ")
    assert result == create_exercise("Squat", "legs")


def test_find_exercise_returns_none_when_missing() -> None:
    result = find_exercise([create_exercise("Squat", "legs")], "Deadlift")
    assert result is None


@pytest.mark.parametrize("reps, expected", [(10, True), (1, True), (0, False), (-3, False)])
def test_reps_must_be_positive(reps: int, expected: bool) -> None:
    assert is_valid_reps(reps) == expected


@pytest.mark.parametrize(
    "weight, expected",
    [
        (30.0, True),
        (0.0, True),
        (-1.0, False),
        (float("nan"), False),
        (float("inf"), False),
        (float("-inf"), False),
    ],
)
def test_weight_must_be_finite_and_non_negative(weight: float, expected: bool) -> None:
    assert is_valid_weight(weight) == expected


def test_first_workout_number_is_one() -> None:
    assert next_workout_id([]) == 1


def test_workout_numbers_increase() -> None:
    assert next_workout_id([Workout(1), Workout(2)]) == 3


def test_current_workout_returns_latest() -> None:
    assert current_workout([Workout(1), Workout(2)]) == Workout(2)


def test_current_workout_is_none_when_empty() -> None:
    assert current_workout([]) is None


def test_find_previous_workout() -> None:
    assert find_workout([Workout(1), Workout(2)], 1) == Workout(1)


def test_find_unknown_workout() -> None:
    assert find_workout([Workout(1), Workout(2)], 5) is None


def test_summary_calculates_sets_reps_and_volume() -> None:
    exercise = create_exercise("Squat", "legs")
    workout_sets = [WorkoutSet("Squat", 10, 50.0, 1), WorkoutSet("Squat", 8, 55.0, 1)]
    result = summarize_exercise(exercise, workout_sets, 1)
    assert result == ExerciseSummary("Squat", "legs", 2, 18, 940.0)


def test_summary_ignores_other_exercises() -> None:
    exercise = create_exercise("Squat", "legs")
    workout_sets = [WorkoutSet("Squat", 10, 50.0, 1), WorkoutSet("Bench Press", 8, 40.0, 1)]
    result = summarize_exercise(exercise, workout_sets, 1)
    assert result == ExerciseSummary("Squat", "legs", 1, 10, 500.0)


def test_summary_ignores_other_workouts() -> None:
    exercise = create_exercise("Squat", "legs")
    workout_sets = [WorkoutSet("Squat", 10, 50.0, 1), WorkoutSet("Squat", 5, 80.0, 2)]
    result = summarize_exercise(exercise, workout_sets, 2)
    assert result == ExerciseSummary("Squat", "legs", 1, 5, 400.0)


def test_summary_with_no_sets() -> None:
    exercise = create_exercise("Squat", "legs")
    result = summarize_exercise(exercise, [], 1)
    assert result == ExerciseSummary("Squat", "legs", 0, 0, 0.0)


def test_summary_accepts_bodyweight_exercises() -> None:
    exercise = create_exercise("Push Up", "chest")
    result = summarize_exercise(exercise, [WorkoutSet("Push Up", 12, 0.0, 1)], 1)
    assert result == ExerciseSummary("Push Up", "chest", 1, 12, 0.0)

import pytest

from gym_workout_logger.workout import (
    create_exercise,
    is_valid_exercise_name,
    is_valid_muscle_group,
    normalize_exercise_name,
    normalize_muscle_group,
)


def test_exercise_name_removes_surrounding_whitespace() -> None:
    assert normalize_exercise_name("  Squat  ") == "Squat"


def test_exercise_muscle_group_removes_surrounding_whitespace() -> None:
    assert normalize_muscle_group("  Legs  ") == "Legs"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Squat", True),
        ("", False),
        ("   ", False),
    ],
)
def test_exercise_name_validation(name: str, expected: bool) -> None:
    result = is_valid_exercise_name(name)

    assert result == expected


@pytest.mark.parametrize(
    ("muscle_group", "expected"),
    [
        ("legs", True),
        ("", False),
        ("   ", False),
    ],
)
def test_muscle_group_validation(muscle_group: str, expected: bool) -> None:
    result = is_valid_muscle_group(muscle_group)

    assert result == expected


def test_create_exercise_removes_surrounding_whitespace() -> None:
    result = create_exercise("  Squat  ", "  legs  ")

    assert result.name == "Squat"
    assert result.muscle_group == "legs"

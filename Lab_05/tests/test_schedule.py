"""Тести варіанта 9: циклічний розклад."""

from collections.abc import Iterator
from itertools import islice

import pytest

from schedule import (
    Day,
    cumulative_hours,
    cyclic_schedule,
    days_until,
    duty_roster,
    plan,
    weekdays_from,
    weeks,
)

SHIFTS = ("A", "B", "C")


def test_plan_numbering_and_cycle() -> None:
    """Тест: нумерація днів, дні тижня і циклічність змін."""
    days = plan(SHIFTS, 5)
    assert [d.number for d in days] == [1, 2, 3, 4, 5]
    assert [d.shift for d in days] == ["A", "B", "C", "A", "B"]
    assert [d.weekday for d in days] == ["Пн", "Вт", "Ср", "Чт", "Пт"]


def test_start_weekday_wraps() -> None:
    """Тест: старт з неділі переходить на понеділок."""
    days = plan(SHIFTS, 2, start_weekday=6)
    assert days == [Day(1, "Нд", "A"), Day(2, "Пн", "B")]


def test_invalid_weekday() -> None:
    """Тест: некоректний день тижня - ValueError."""
    with pytest.raises(ValueError):
        weekdays_from(7)


def test_zero_days_and_empty_shifts() -> None:
    """Тест: n=0 і порожнє джерело змін."""
    assert plan(SHIFTS, 0) == []
    assert plan([], 5) == []


def test_schedule_is_infinite_but_lazy() -> None:
    """Тест: нескінченний розклад можна безпечно обмежити islice."""
    far = list(islice(cyclic_schedule(SHIFTS), 1000, 1001))
    assert far == [Day(1001, "Нд", "B")]


def test_laziness_counts_pulled_items() -> None:
    """Тест: з джерела змін береться рівно стільки, скільки потрібно."""
    pulled: list[str] = []

    def source() -> Iterator[str]:
        """Джерело змін, що запам'ятовує кожне звернення."""
        for shift in ("A", "B", "C", "D", "E"):
            pulled.append(shift)
            yield shift

    schedule = cyclic_schedule(source())
    assert pulled == []
    assert [d.shift for d in islice(schedule, 3)] == ["A", "B", "C"]
    assert pulled == ["A", "B", "C"]


def test_duty_roster() -> None:
    """Тест: працівники і зміни чергуються незалежно."""
    roster = list(islice(duty_roster(["X", "Y"], SHIFTS), 4))
    assert [(d.worker, d.shift) for d in roster] == [
        ("X", "A"),
        ("Y", "B"),
        ("X", "C"),
        ("Y", "A"),
    ]


def test_days_until() -> None:
    """Тест: takewhile до першої потрібної зміни."""
    assert len(days_until(SHIFTS, "C")) == 2
    assert days_until(SHIFTS, "A") == []
    assert len(days_until(SHIFTS, "Z", limit=10)) == 10


def test_weeks_chunked() -> None:
    """Тест: групування по 7 днів."""
    two = weeks(SHIFTS, 2)
    assert len(two) == 2 and all(len(w) == 7 for w in two)
    assert two[1][0].number == 8


def test_cumulative_hours() -> None:
    """Тест: накопичені години через accumulate."""
    hours = {"A": 8.0, "B": 10.0}
    assert cumulative_hours(SHIFTS, hours, 4) == [8.0, 18.0, 18.0, 26.0]

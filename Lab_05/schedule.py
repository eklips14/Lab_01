"""Варіант 9 ЛР5: нескінченний циклічний розклад змін.

Розклад будується ліниво з cycle, count, zip та islice. Значення
обчислюються лише тоді, коли їх запитують.
"""

from collections.abc import Iterable, Iterator, Mapping
from itertools import accumulate, count, cycle, islice, takewhile
from typing import NamedTuple

from streams import chunked, take

WEEKDAYS: tuple[str, ...] = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд")


class Day(NamedTuple):
    """Один день розкладу."""

    number: int
    weekday: str
    shift: str


class Duty(NamedTuple):
    """Чергування працівника в конкретний день."""

    number: int
    worker: str
    shift: str


def weekdays_from(start_weekday: int = 0) -> Iterator[str]:
    """Нескінченний потік днів тижня, починаючи з заданого (0 - понеділок)."""
    if not 0 <= start_weekday < len(WEEKDAYS):
        raise ValueError("start_weekday має бути в межах 0..6")
    return islice(cycle(WEEKDAYS), start_weekday, None)


def cyclic_schedule(shifts: Iterable[str], start_weekday: int = 0) -> Iterator[Day]:
    """Нескінченний розклад: нумерація count, дні тижня і зміни через cycle."""
    days = weekdays_from(start_weekday)
    return (Day(n, wd, s) for n, wd, s in zip(count(1), days, cycle(shifts)))


def plan(shifts: Iterable[str], days: int, start_weekday: int = 0) -> list[Day]:
    """План на N днів (матеріалізуються лише N елементів)."""
    return take(days, cyclic_schedule(shifts, start_weekday))


def duty_roster(workers: Iterable[str], shifts: Iterable[str]) -> Iterator[Duty]:
    """Нескінченний графік чергувань: працівники і зміни чергуються циклічно."""
    return (Duty(n, w, s) for n, w, s in zip(count(1), cycle(workers), cycle(shifts)))


def days_until(shifts: Iterable[str], target: str, limit: int = 366) -> list[Day]:
    """Дні до першої появи зміни target (takewhile), не більше limit днів."""
    schedule = islice(cyclic_schedule(shifts), limit)
    return list(takewhile(lambda d: d.shift != target, schedule))


def weeks(shifts: Iterable[str], n_weeks: int) -> list[tuple[Day, ...]]:
    """Розклад, згрупований по тижнях (ліниві пакети по 7 днів)."""
    return take(n_weeks, chunked(cyclic_schedule(shifts), 7))


def cumulative_hours(
    shifts: Iterable[str], hours: Mapping[str, float], days: int
) -> list[float]:
    """Накопичені робочі години за N днів через accumulate."""
    return list(accumulate(hours.get(d.shift, 0.0) for d in plan(shifts, days)))

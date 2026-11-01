"""pytest-тести ЛР2, варіант 9."""

from copy import deepcopy

import pytest

from core import (
    Employee,
    at_least_hours,
    boost_department,
    build_pipeline,
    compose,
    normalize_names,
    pipe,
    reduce_stats,
    sort_by_hours_desc,
    take,
    with_total_hours,
)


@pytest.fixture
def employees() -> list[Employee]:
    """Тестові записи працівників."""
    return [
        {"id": 1, "name": " ivan ", "department": "IT", "monthly_hours": [100, 100]},
        {"id": 2, "name": "olena", "department": "HR", "monthly_hours": [150, 150]},
        {"id": 3, "name": "petro", "department": "IT", "monthly_hours": [50, 50]},
        {"id": 4, "name": "maria", "department": "HR", "monthly_hours": [100, 100]},
    ]


def test_top_n(employees: list[Employee]) -> None:
    """Тест: Top-N з коефіцієнтом відділу і фільтром."""
    pipeline = build_pipeline(top_n=2, department="IT", factor=1.5, min_hours=150)
    result = list(pipeline(employees))
    assert [e["id"] for e in result] == [1, 2]
    assert result[0]["total_hours"] == pytest.approx(300.0)
    assert result[0]["name"] == "Ivan"


def test_no_mutation(employees: list[Employee]) -> None:
    """Тест: вхідні записи не змінюються."""
    original = deepcopy(employees)
    list(build_pipeline(top_n=3)(employees))
    assert employees == original
    assert all("total_hours" not in e for e in employees)


def test_reduce_stats(employees: list[Employee]) -> None:
    """Тест: правильність reduce-агрегації."""
    stats = reduce_stats(with_total_hours()(employees))
    assert stats == {"count": 4, "total_hours": 800.0, "avg_hours": 200.0}


def test_reduce_stats_empty() -> None:
    """Тест: агрегація порожнього списку."""
    assert reduce_stats([]) == {"count": 0, "total_hours": 0.0, "avg_hours": 0.0}


def test_compose_order() -> None:
    """Тест: compose застосовує функції справа наліво, pipe зліва направо."""
    first = take(1)
    ordered = sort_by_hours_desc()
    data: list[Employee] = [
        {"id": 1, "total_hours": 10.0},
        {"id": 2, "total_hours": 20.0},
    ]
    assert [e["id"] for e in compose(first, ordered)(data)] == [2]
    assert [e["id"] for e in pipe(ordered, first)(data)] == [2]
    assert [e["id"] for e in compose(ordered, first)(data)] == [1]


def test_sort_tie_breaker() -> None:
    """Тест: при рівних годинах сортування за id зростанням."""
    data: list[Employee] = [
        {"id": 3, "total_hours": 5.0},
        {"id": 1, "total_hours": 5.0},
        {"id": 2, "total_hours": 9.0},
    ]
    assert [e["id"] for e in sort_by_hours_desc()(data)] == [2, 1, 3]


def test_boost_only_selected_department(employees: list[Employee]) -> None:
    """Тест: коефіцієнт застосовується лише до вибраного відділу."""
    stage = compose(boost_department("HR", 2.0), with_total_hours())
    hours = {e["id"]: e["total_hours"] for e in stage(employees)}
    assert hours == {1: 200.0, 2: 600.0, 3: 100.0, 4: 400.0}


def test_filter_min_hours(employees: list[Employee]) -> None:
    """Тест: фільтр за мінімальною кількістю годин."""
    stage = compose(at_least_hours(200), with_total_hours())
    assert [e["id"] for e in stage(employees)] == [1, 2, 4]


def test_normalize_names(employees: list[Employee]) -> None:
    """Тест: нормалізація імен."""
    assert [e["name"] for e in normalize_names()(employees)] == [
        "Ivan",
        "Olena",
        "Petro",
        "Maria",
    ]


def test_take_zero_and_negative(employees: list[Employee]) -> None:
    """Тест: take(0) і від'ємне n дають порожній список."""
    assert take(0)(employees) == []
    assert take(-1)(employees) == []

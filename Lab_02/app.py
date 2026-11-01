"""Оболонка ЛР2 (I/O та CLI): читання аргументів, даних і друк результатів."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from core import Employee, build_pipeline, reduce_stats, with_total_hours


def sample_employees() -> list[Employee]:
    """Демонстраційні дані працівників."""
    return [
        {
            "id": 1,
            "name": "ivan petrenko",
            "department": "IT",
            "monthly_hours": [160, 168, 172],
        },
        {
            "id": 2,
            "name": "olena koval",
            "department": "HR",
            "monthly_hours": [150, 140, 155],
        },
        {
            "id": 3,
            "name": "andrii melnyk",
            "department": "IT",
            "monthly_hours": [120, 130, 125],
        },
        {
            "id": 4,
            "name": "maria shevchenko",
            "department": "Sales",
            "monthly_hours": [176, 180, 170],
        },
        {
            "id": 5,
            "name": "taras bondar",
            "department": "Sales",
            "monthly_hours": [100, 90, 95],
        },
        {
            "id": 6,
            "name": "iryna lysenko",
            "department": "IT",
            "monthly_hours": [158, 162, 160],
        },
    ]


def load_employees(path: Path) -> list[Employee]:
    """Читає список працівників із JSON-файлу."""
    with path.open(encoding="utf-8") as source:
        data: list[Employee] = json.load(source)
    return data


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Розбирає аргументи командного рядка."""
    parser = argparse.ArgumentParser(description="Top-N працівників за годинами")
    parser.add_argument("--data", type=Path, default=None, help="JSON з даними")
    parser.add_argument("--top", type=int, default=3, help="кількість записів")
    parser.add_argument("--boost-dept", default="IT", help="відділ з коефіцієнтом")
    parser.add_argument("--factor", type=float, default=1.1, help="коефіцієнт")
    parser.add_argument("--min-hours", type=float, default=400.0, help="мінімум годин")
    return parser.parse_args(argv)


def render(top: Sequence[Employee], employees: Sequence[Employee]) -> None:
    """Друкує рейтинг і статистику."""
    print(f"{'ID':>3} {'Ім`я':<18} {'Відділ':<7} {'Години':>8}")
    for e in top:
        print(
            f"{e['id']:>3} {e['name']:<18} {e['department']:<7} "
            f"{e['total_hours']:>8.1f}"
        )
    stats = reduce_stats(with_total_hours()(employees))
    print(
        f"\nВсі працівники: count={stats['count']}, "
        f"total_hours={stats['total_hours']:.1f}, avg_hours={stats['avg_hours']:.1f}"
    )
    top_stats = reduce_stats(top)
    print(
        f"Top-N: count={top_stats['count']}, "
        f"total_hours={top_stats['total_hours']:.1f}, "
        f"avg_hours={top_stats['avg_hours']:.1f}"
    )


def run(argv: Sequence[str] | None = None) -> None:
    """Запускає конвеєр з параметрами з командного рядка."""
    args = parse_args(argv)
    employees = load_employees(args.data) if args.data else sample_employees()
    pipeline = build_pipeline(
        top_n=args.top,
        department=args.boost_dept,
        factor=args.factor,
        min_hours=args.min_hours,
    )
    render(list(pipeline(employees)), employees)


if __name__ == "__main__":
    run()

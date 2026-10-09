"""Оболонка побічних ефектів (I/O shell) для варіанта 9 - прокат автомобілів.

Тут і ТІЛЬКИ тут живуть побічні ефекти: читання файлу, print, time.time.
Ядро (core.py) лише отримує дані й повертає новий результат.

Запуск:
    python app.py                 # дані з data/rentals.json
    python app.py шлях/до/файлу   # інший JSON-файл
"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

from core import (
    Rental,
    Report,
    lift_price_fn,
    make_class_insurance,
    make_coupon,
    make_duration_discount,
    make_min_days_filter,
    make_per_day_insurance,
    make_percent_off,
    make_processor,
    pipe,
    process_rentals_pure,
    stamp_report,
    totals_by_class,
)

DATA_FILE = Path(__file__).with_name("data") / "rentals.json"

# Конфігурація політик - звичайні дані, які передаються в ядро явно.
DISCOUNT_TIERS: Sequence[tuple[int, float]] = ((7, 0.10), (14, 0.15), (30, 0.25))
INSURANCE_RATES = {
    "economy": 0.05,
    "comfort": 0.08,
    "business": 0.12,
    "premium": 0.18,
}


# ---------------------------------------------------------------------------
# I/O: читання
# ---------------------------------------------------------------------------


def load_rentals(path: Path) -> list[Rental]:
    """Читає список прокатів із JSON-файлу (побічний ефект - файл)."""
    with path.open(encoding="utf-8") as fh:
        data: list[Rental] = json.load(fh)
    return data


# ---------------------------------------------------------------------------
# I/O: рендеринг звіту (лише споживає чистий результат)
# ---------------------------------------------------------------------------


def render_report(title: str, report: Report) -> None:
    """Друкує звіт. Нічого не обчислює і нічого не змінює."""
    print(f"=== {title} ===")
    print(
        f"{'ID':>4} {'Клас':<10} {'Днів':>4} {'База':>10} {'Знижка':>9} "
        f"{'Страх.':>9} {'Разом':>10}"
    )
    for r in report["rentals"]:
        print(
            f"{r['id']:>4} {r['car_class']:<10} {r['days']:>4} "
            f"{r['base_price']:>10.2f} {r['discount']:>9.2f} "
            f"{r['insurance']:>9.2f} {r['total']:>10.2f}"
        )
    print(f"Прийнято прокатів: {report['count']}")
    print(f"Дохід:            {report['revenue']:.2f}")
    by_class = totals_by_class(report["rentals"])
    for cls, total in by_class.items():
        print(f"  {cls:<10} {total:>10.2f}")
    print()


def render_stamped(report: Report) -> None:
    """Демонстрація інжекції часу: time.time передається в ядро як Callable."""
    stamped = stamp_report(report, time.time)
    ts = float(str(stamped["generated_at"]))
    when = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")
    print(f"Звіт сформовано: {when} (UTC)")
    print()


# ---------------------------------------------------------------------------
# Точка входу
# ---------------------------------------------------------------------------


def run(rentals: Sequence[Rental]) -> None:
    # Завдання 1: чиста функція з явними параметрами (без глобалів).
    basic = process_rentals_pure(
        rentals,
        min_days=2,
        discount_tiers=DISCOUNT_TIERS,
        insurance_rates=INSURANCE_RATES,
        default_insurance_rate=0.10,
    )
    render_report("Завдання 1: process_rentals_pure", basic)

    # Завдання 2: той самий розрахунок через фабрику з Callable-політиками.
    standard = make_processor(
        accept=make_min_days_filter(2),
        apply_discount=make_duration_discount(DISCOUNT_TIERS),
        insurance_fee=make_class_insurance(INSURANCE_RATES, default=0.10),
    )
    render_report("Завдання 2: make_processor (стандартні політики)", standard(rentals))

    # Інша конфігурація: купон + відсоткова знижка (compose/pipe),
    # фіксована страховка за день, без обмеження на тривалість.
    promo_discount = pipe(make_percent_off(5), make_coupon(50.0))
    promo = make_processor(
        accept=make_min_days_filter(1),
        apply_discount=lift_price_fn(promo_discount),
        insurance_fee=make_per_day_insurance(15.0),
    )
    render_report("Завдання 2: make_processor (акційні політики)", promo(rentals))

    # Завдання 3: час приходить ззовні, ядро лишається чистим.
    render_stamped(basic)


def main(argv: Sequence[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DATA_FILE
    try:
        rentals = load_rentals(path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Не вдалося прочитати {path}: {exc}", file=sys.stderr)
        return 1
    run(rentals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

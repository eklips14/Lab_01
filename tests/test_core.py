"""pytest-тести чистого ядра (варіант 9 - прокат автомобілів)."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy

import pytest

from core import (
    DiscountFn,
    InsuranceFn,
    Rental,
    Report,
    base_price,
    compose,
    duration_discount_rate,
    insurance_rate_for,
    lift_price_fn,
    make_class_insurance,
    make_coupon,
    make_duration_discount,
    make_min_days_filter,
    make_multiplier,
    make_per_day_insurance,
    make_percent_off,
    make_processor,
    mark_cancelled,
    pipe,
    process_rentals_pure,
    stamp_report,
    stamp_total,
    totals_by_class,
    with_pricing,
)

TIERS = ((7, 0.10), (30, 0.25))
RATES = {"economy": 0.05, "comfort": 0.08, "business": 0.12, "premium": 0.18}


def run_pure(rentals: list[Rental]) -> Report:
    """Стандартна конфігурація process_rentals_pure для тестів."""
    return process_rentals_pure(
        rentals,
        min_days=2,
        discount_tiers=TIERS,
        insurance_rates=RATES,
        default_insurance_rate=0.10,
    )


# ---------------------------------------------------------------------------
# Референтна прозорість та відсутність мутацій
# ---------------------------------------------------------------------------


def test_referential_transparency(sample_rentals: list[Rental]) -> None:
    r1 = run_pure(sample_rentals)
    r2 = run_pure(sample_rentals)
    assert r1 == r2  # той самий вхід -> той самий вихід


def test_no_mutation(sample_rentals: list[Rental]) -> None:
    original = deepcopy(sample_rentals)
    run_pure(sample_rentals)
    assert sample_rentals == original  # вхід не змінюється


def test_result_records_are_new_objects(sample_rentals: list[Rental]) -> None:
    result = run_pure(sample_rentals)
    inputs = {id(r) for r in sample_rentals}
    assert all(id(r) not in inputs for r in result["rentals"])
    assert all("total" not in r for r in sample_rentals)


def test_processor_no_mutation(sample_rentals: list[Rental]) -> None:
    original = deepcopy(sample_rentals)
    processor = make_processor(
        accept=make_min_days_filter(0),
        apply_discount=make_duration_discount(TIERS),
        insurance_fee=make_class_insurance(RATES, default=0.1),
    )
    processor(sample_rentals)
    assert sample_rentals == original


# ---------------------------------------------------------------------------
# Коректність обчислень
# ---------------------------------------------------------------------------


def test_base_price() -> None:
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "days": 3,
        "daily_rate": 100.0,
        "status": "confirmed",
    }
    assert base_price(rental) == 300.0


def test_duration_discount_rate() -> None:
    assert duration_discount_rate(3, TIERS) == 0.0
    assert duration_discount_rate(7, TIERS) == 0.10
    assert duration_discount_rate(29, TIERS) == 0.10
    assert duration_discount_rate(30, TIERS) == 0.25
    assert duration_discount_rate(100, ()) == 0.0


def test_insurance_rate_for() -> None:
    assert insurance_rate_for("premium", RATES, 0.1) == 0.18
    assert insurance_rate_for("unknown", RATES, 0.1) == 0.1


def test_with_pricing_returns_new_dict() -> None:
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "days": 3,
        "daily_rate": 100.0,
        "status": "confirmed",
    }
    priced = with_pricing(rental, base=300.0, discount=30.0, insurance=13.5)
    assert priced is not rental
    assert "total" not in rental
    assert priced["total"] == pytest.approx(283.5)
    assert priced["id"] == 1


def test_process_rentals_pure_values(sample_rentals: list[Rental]) -> None:
    result = run_pure(sample_rentals)
    # Відкинуто: id=3 (1 день < 2), id=5 (cancelled), id=6 (pending)
    assert [r["id"] for r in result["rentals"]] == [1, 2, 4]
    assert result["count"] == 3

    by_id = {r["id"]: r for r in result["rentals"]}
    # id=1: 3*100 = 300, знижка 0, страх. 5% -> 315
    assert by_id[1]["total"] == pytest.approx(315.0)
    # id=2: 7*200 = 1400, знижка 10% = 140 -> 1260, страх. 8% = 100.8 -> 1360.8
    assert by_id[2]["discount"] == pytest.approx(140.0)
    assert by_id[2]["total"] == pytest.approx(1360.8)
    # id=4: 30*400 = 12000, знижка 25% = 3000 -> 9000, страх. 18% = 1620 -> 10620
    assert by_id[4]["total"] == pytest.approx(10620.0)

    assert result["revenue"] == pytest.approx(315.0 + 1360.8 + 10620.0)


# ---------------------------------------------------------------------------
# Callable-політики
# ---------------------------------------------------------------------------


def test_callable_policies(sample_rentals: list[Rental]) -> None:
    accept = lambda r: r["status"] == "confirmed" and base_price(r) >= 500  # noqa: E731
    apply_discount: DiscountFn = lambda r, p: p * 0.9  # noqa: E731
    insurance_fee: InsuranceFn = lambda r, p: p * 0.2  # noqa: E731

    processor = make_processor(
        accept=accept, apply_discount=apply_discount, insurance_fee=insurance_fee
    )
    result = processor(sample_rentals)

    # Пройшли: id=2 (1400), id=3 (500), id=4 (12000); id=1 (300) - відкинуто
    assert [r["id"] for r in result["rentals"]] == [2, 3, 4]
    expected = sum(b * 0.9 * 1.2 for b in (1400.0, 500.0, 12000.0))
    assert result["revenue"] == pytest.approx(expected)


def test_processor_matches_pure_version(sample_rentals: list[Rental]) -> None:
    processor = make_processor(
        accept=make_min_days_filter(2),
        apply_discount=make_duration_discount(TIERS),
        insurance_fee=make_class_insurance(RATES, default=0.10),
    )
    assert processor(sample_rentals) == run_pure(sample_rentals)


def test_swapping_policy_changes_only_that_part(sample_rentals: list[Rental]) -> None:
    accept = make_min_days_filter(2)
    discount = make_duration_discount(TIERS)
    percent = make_processor(
        accept=accept,
        apply_discount=discount,
        insurance_fee=make_class_insurance(RATES, 0.1),
    )
    per_day = make_processor(
        accept=accept,
        apply_discount=discount,
        insurance_fee=make_per_day_insurance(10.0),
    )

    p, d = percent(sample_rentals), per_day(sample_rentals)
    assert [r["id"] for r in p["rentals"]] == [r["id"] for r in d["rentals"]]
    for a, b in zip(p["rentals"], d["rentals"], strict=True):
        assert a["discount"] == pytest.approx(b["discount"])
        assert b["insurance"] == pytest.approx(b["days"] * 10.0)


def test_make_duration_discount_is_isolated_from_later_changes() -> None:
    tiers = [(7, 0.5)]
    policy = make_duration_discount(tiers)
    tiers.append((1, 0.99))  # зміна зовнішнього списку не впливає на політику
    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "days": 2,
        "daily_rate": 10.0,
        "status": "confirmed",
    }
    assert policy(rental, 20.0) == 20.0


# ---------------------------------------------------------------------------
# Інжекція залежностей (час)
# ---------------------------------------------------------------------------


def test_stamp_total_uses_injected_clock() -> None:
    fake_now = lambda: 1_700_000_000.0  # noqa: E731
    assert stamp_total(99.0, fake_now) == (99.0, 1_700_000_000.0)
    assert stamp_total(99.0, fake_now) == stamp_total(99.0, fake_now)


def test_stamp_report_does_not_mutate(sample_rentals: list[Rental]) -> None:
    report = run_pure(sample_rentals)
    before = deepcopy(report)
    stamped = stamp_report(report, lambda: 1.0)
    assert report == before
    assert stamped["generated_at"] == 1.0
    assert "generated_at" not in report


# ---------------------------------------------------------------------------
# Додаткові вправи
# ---------------------------------------------------------------------------


def test_compose() -> None:
    inc: Callable[[int], int] = lambda x: x + 1  # noqa: E731
    dbl: Callable[[int], int] = lambda x: x * 2  # noqa: E731
    assert compose(inc, dbl)(5) == 11  # inc(dbl(5))
    assert compose(dbl, inc)(5) == 12  # dbl(inc(5))


def test_pipe_builds_discount_from_small_functions() -> None:
    discount = pipe(make_percent_off(10), make_coupon(20.0))
    assert discount(200.0) == pytest.approx(160.0)  # 200*0.9 = 180, -20 = 160
    assert make_coupon(500.0)(100.0) == 0.0  # не від'ємна

    rental: Rental = {
        "id": 1,
        "car_class": "economy",
        "days": 1,
        "daily_rate": 200.0,
        "status": "confirmed",
    }
    assert lift_price_fn(discount)(rental, 200.0) == pytest.approx(160.0)


def test_make_multiplier() -> None:
    triple = make_multiplier(3)
    assert triple(5) == 15
    assert [make_multiplier(k)(2) for k in (1, 2, 3)] == [2, 4, 6]


def test_mark_cancelled_returns_new_list(sample_rentals: list[Rental]) -> None:
    original = deepcopy(sample_rentals)
    updated = mark_cancelled(sample_rentals, [1, 2])
    assert sample_rentals == original
    assert updated is not sample_rentals
    assert [r["status"] for r in updated[:2]] == ["cancelled", "cancelled"]
    assert updated[2] is sample_rentals[2]  # незмінені записи можна ділити


def test_totals_by_class(sample_rentals: list[Rental]) -> None:
    result = run_pure(sample_rentals)
    totals = totals_by_class(result["rentals"])
    assert set(totals) == {"economy", "comfort", "premium"}
    assert sum(totals.values()) == pytest.approx(result["revenue"])

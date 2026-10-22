from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TypedDict, TypeVar


class Rental(TypedDict, total=False):
    id: int
    car_class: str
    days: int
    daily_rate: float
    status: str
    base_price: float
    discount: float
    insurance: float
    total: float


class Report(TypedDict):
    count: int
    revenue: float
    rentals: list[Rental]


PriceFn = Callable[[float], float]
DiscountFn = Callable[[Rental, float], float]
InsuranceFn = Callable[[Rental, float], float]
AcceptFn = Callable[[Rental], bool]
NowFn = Callable[[], float]
Processor = Callable[[Iterable[Rental]], Report]


def base_price(rental: Rental) -> float:
    return rental["days"] * rental["daily_rate"]


def is_confirmed(rental: Rental) -> bool:
    return rental["status"] == "confirmed"


def duration_discount_rate(days: int, tiers: Sequence[tuple[int, float]]) -> float:
    reached = [rate for min_days, rate in tiers if days >= min_days]
    return max(reached, default=0.0)


def insurance_rate_for(
    car_class: str, rates: Mapping[str, float], default: float
) -> float:
    return rates.get(car_class, default)


def with_pricing(
    rental: Rental, *, base: float, discount: float, insurance: float
) -> Rental:
    return {
        **rental,
        "base_price": base,
        "discount": discount,
        "insurance": insurance,
        "total": base - discount + insurance,
    }


def summarize(rentals: Sequence[Rental]) -> Report:
    return {
        "count": len(rentals),
        "revenue": sum(r["total"] for r in rentals),
        "rentals": list(rentals),
    }


def process_rentals_pure(
    rentals: Iterable[Rental],
    *,
    min_days: int,
    discount_tiers: Sequence[tuple[int, float]],
    insurance_rates: Mapping[str, float],
    default_insurance_rate: float,
) -> Report:
    confirmed = (r for r in rentals if is_confirmed(r))
    qualified = (r for r in confirmed if r["days"] >= min_days)

    priced: list[Rental] = []
    for r in qualified:
        base = base_price(r)
        discount = base * duration_discount_rate(r["days"], discount_tiers)
        discounted = base - discount
        insurance = discounted * insurance_rate_for(
            r["car_class"], insurance_rates, default_insurance_rate
        )
        priced.append(
            with_pricing(r, base=base, discount=discount, insurance=insurance)
        )

    return summarize(priced)


def make_processor(
    *,
    accept: AcceptFn,
    apply_discount: DiscountFn,
    insurance_fee: InsuranceFn,
) -> Processor:

    def price_one(rental: Rental) -> Rental:
        base = base_price(rental)
        discounted = apply_discount(rental, base)
        fee = insurance_fee(rental, discounted)
        return with_pricing(
            rental, base=base, discount=base - discounted, insurance=fee
        )

    def process(rentals: Iterable[Rental]) -> Report:
        priced = [price_one(r) for r in rentals if accept(r)]
        return summarize(priced)

    return process


def make_min_days_filter(min_days: int) -> AcceptFn:
    return lambda r: is_confirmed(r) and r["days"] >= min_days


def make_duration_discount(tiers: Sequence[tuple[int, float]]) -> DiscountFn:
    frozen = tuple(tiers)
    return lambda r, price: price * (1 - duration_discount_rate(r["days"], frozen))


def make_class_insurance(
    rates: Mapping[str, float], default: float = 0.0
) -> InsuranceFn:
    frozen = dict(rates)
    return lambda r, price: price * insurance_rate_for(r["car_class"], frozen, default)


def make_per_day_insurance(fee_per_day: float) -> InsuranceFn:
    return lambda r, _price: r["days"] * fee_per_day


def lift_price_fn(fn: PriceFn) -> DiscountFn:
    return lambda _r, price: fn(price)


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    return total, now()


def stamp_report(report: Report, now: NowFn) -> dict[str, object]:
    return {**report, "generated_at": now()}


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def pipe(*fns: PriceFn) -> PriceFn:
    def identity(x: float) -> float:
        return x

    result: PriceFn = identity
    for fn in fns:
        result = compose(fn, result)
    return result


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k


def make_percent_off(percent: float) -> PriceFn:
    return lambda price: price * (1 - percent / 100)


def make_coupon(amount: float) -> PriceFn:
    return lambda price: max(0.0, price - amount)


def mark_cancelled(rentals: Sequence[Rental], ids: Iterable[int]) -> list[Rental]:
    to_cancel = frozenset(ids)
    return [
        {**r, "status": "cancelled"} if r["id"] in to_cancel else r for r in rentals
    ]


def totals_by_class(rentals: Sequence[Rental]) -> dict[str, float]:
    classes = sorted({r["car_class"] for r in rentals})
    return {
        cls: sum(r["total"] for r in rentals if r["car_class"] == cls)
        for cls in classes
    }

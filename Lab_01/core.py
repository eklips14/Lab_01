from collections.abc import Iterable, Mapping, Sequence
from typing import Callable, TypedDict  # noqa: UP035


class Rental(TypedDict, total=False):
    """Запис про прокат автомобіля."""

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
    """Результат обробки: кількість, дохід і нові записи."""

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
    """Базова ціна: кількість днів помножена на денну ставку."""
    return rental["days"] * rental["daily_rate"]


def is_confirmed(rental: Rental) -> bool:
    """Перевіряє, чи прокат підтверджено."""
    return rental["status"] == "confirmed"


def duration_discount_rate(days: int, tiers: Sequence[tuple[int, float]]) -> float:
    """Ставка знижки за тривалістю прокату."""
    reached = [rate for min_days, rate in tiers if days >= min_days]
    return max(reached, default=0.0)


def insurance_rate_for(
    car_class: str, rates: Mapping[str, float], default: float
) -> float:
    """Ставка страхового збору для класу авто."""
    return rates.get(car_class, default)


def with_pricing(
    rental: Rental, *, base: float, discount: float, insurance: float
) -> Rental:
    """Створює новий запис з цінами (без мутації вхідного словника)."""
    return {
        **rental,
        "base_price": base,
        "discount": discount,
        "insurance": insurance,
        "total": base - discount + insurance,
    }


def summarize(rentals: Sequence[Rental]) -> Report:
    """Формує звіт з оброблених записів."""
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
    """Чиста обробка прокатів з явно переданими параметрами."""
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
    """Фабрика, яка створює обробник з Callable-політиками."""

    def price_one(rental: Rental) -> Rental:
        """Обчислює ціну одного прокату."""
        base = base_price(rental)
        discounted = apply_discount(rental, base)
        fee = insurance_fee(rental, discounted)
        return with_pricing(
            rental, base=base, discount=base - discounted, insurance=fee
        )

    def process(rentals: Iterable[Rental]) -> Report:
        """Обробляє список прокатів."""
        priced = [price_one(r) for r in rentals if accept(r)]
        return summarize(priced)

    return process


def make_min_days_filter(min_days: int) -> AcceptFn:
    """Політика фільтра: підтверджені прокати від min_days днів."""
    return lambda r: is_confirmed(r) and r["days"] >= min_days


def make_duration_discount(tiers: Sequence[tuple[int, float]]) -> DiscountFn:
    """Політика знижки за тривалістю."""
    frozen = tuple(tiers)
    return lambda r, price: price * (1 - duration_discount_rate(r["days"], frozen))


def make_class_insurance(
    rates: Mapping[str, float], default: float = 0.0
) -> InsuranceFn:
    """Політика страхування у відсотках за класом авто."""
    frozen = dict(rates)
    return lambda r, price: price * insurance_rate_for(r["car_class"], frozen, default)


def make_per_day_insurance(fee_per_day: float) -> InsuranceFn:
    """Політика страхування: фіксована сума за день."""
    return lambda r, _price: r["days"] * fee_per_day


def lift_price_fn(fn: PriceFn) -> DiscountFn:
    """Перетворює функцію ціни на політику знижки."""
    return lambda _r, price: fn(price)


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    """Повертає суму і час, отриманий через інжектовану функцію."""
    return total, now()


def stamp_report(report: Report, now: NowFn) -> dict[str, object]:
    """Повертає новий звіт з позначкою часу."""
    return {**report, "generated_at": now()}


def compose[A, B, C](f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Композиція функцій: compose(f, g)(x) == f(g(x))."""
    return lambda x: f(g(x))


def pipe(*fns: PriceFn) -> PriceFn:
    """Послідовно застосовує функції зліва направо."""

    def identity(x: float) -> float:
        """Повертає аргумент без змін."""
        return x

    result: PriceFn = identity
    for fn in fns:
        result = compose(fn, result)
    return result


def make_multiplier(k: int) -> Callable[[int], int]:
    """Фабрика множників."""
    return lambda x: x * k


def make_percent_off(percent: float) -> PriceFn:
    """Знижка у відсотках."""
    return lambda price: price * (1 - percent / 100)


def make_coupon(amount: float) -> PriceFn:
    """Купон на фіксовану суму."""
    return lambda price: max(0.0, price - amount)


def mark_cancelled(rentals: Sequence[Rental], ids: Iterable[int]) -> list[Rental]:
    """Повертає новий список зі скасованими прокатами."""
    to_cancel = frozenset(ids)
    return [
        {**r, "status": "cancelled"} if r["id"] in to_cancel else r for r in rentals
    ]


def totals_by_class(rentals: Sequence[Rental]) -> dict[str, float]:
    """Сума total за класами авто."""
    classes = sorted({r["car_class"] for r in rentals})
    return {
        cls: sum(r["total"] for r in rentals if r["car_class"] == cls)
        for cls in classes
    }

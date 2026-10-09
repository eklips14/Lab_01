"""Чисте ядро предметної області «Прокат автомобілів» (варіант 9).

Усі функції в цьому модулі:

* детерміновані - однаковий вхід завжди дає однаковий вихід;
* не змінюють вхідні дані - завжди повертають нові об'єкти;
* не виконують I/O (жодного print, файлів, мережі);
* не використовують глобальний стан - усі параметри передаються явно
  або інжектуються через ``typing.Callable``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TypedDict, TypeVar

# ---------------------------------------------------------------------------
# Типи предметної області
# ---------------------------------------------------------------------------


class Rental(TypedDict, total=False):
    """Запис про прокат автомобіля.

    Поля ``base_price``, ``discount``, ``insurance`` та ``total``
    відсутні у вхідних даних і з'являються лише у результаті обробки.
    """

    id: int
    car_class: str  # "economy" | "comfort" | "business" | "premium"
    days: int
    daily_rate: float
    status: str  # "confirmed" | "pending" | "cancelled"
    base_price: float
    discount: float
    insurance: float
    total: float


class Report(TypedDict):
    """Підсумок обробки: кількість, сумарний дохід і нові записи."""

    count: int
    revenue: float
    rentals: list[Rental]


# Політики, що передаються як функції (typing.Callable)
PriceFn = Callable[[float], float]  # (price) -> price
DiscountFn = Callable[[Rental, float], float]  # (rental, base_price) -> discounted
InsuranceFn = Callable[[Rental, float], float]  # (rental, discounted) -> fee
AcceptFn = Callable[[Rental], bool]  # (rental) -> чи брати до розрахунку
NowFn = Callable[[], float]  # () -> поточний час (інжекція залежності)
Processor = Callable[[Iterable[Rental]], Report]


# ---------------------------------------------------------------------------
# Базові чисті функції предметної області
# ---------------------------------------------------------------------------


def base_price(rental: Rental) -> float:
    """Базова вартість прокату: кількість днів x денна ставка."""
    return rental["days"] * rental["daily_rate"]


def is_confirmed(rental: Rental) -> bool:
    """Чи підтверджено прокат (аналог ознаки «оплачено»)."""
    return rental["status"] == "confirmed"


def duration_discount_rate(days: int, tiers: Sequence[tuple[int, float]]) -> float:
    """Ставка знижки за тривалість.

    ``tiers`` - послідовність пар ``(мінімальна_кількість_днів, ставка)``.
    Обирається найбільша ставка серед порогів, які досягнуто.
    Якщо жоден поріг не досягнуто - 0.0.
    """
    reached = [rate for min_days, rate in tiers if days >= min_days]
    return max(reached, default=0.0)


def insurance_rate_for(
    car_class: str, rates: Mapping[str, float], default: float
) -> float:
    """Ставка страхового збору для класу авто (або ``default``)."""
    return rates.get(car_class, default)


def with_pricing(
    rental: Rental, *, base: float, discount: float, insurance: float
) -> Rental:
    """Повертає НОВИЙ запис із доданими полями ціни. Вхідний не чіпаємо."""
    return {
        **rental,
        "base_price": base,
        "discount": discount,
        "insurance": insurance,
        "total": base - discount + insurance,
    }


def summarize(rentals: Sequence[Rental]) -> Report:
    """Збирає звіт з уже оцінених записів (без мутацій, без I/O)."""
    return {
        "count": len(rentals),
        "revenue": sum(r["total"] for r in rentals),
        "rentals": list(rentals),
    }


# ---------------------------------------------------------------------------
# Завдання 1: переписаний process_rentals - усі параметри явні
# ---------------------------------------------------------------------------


def process_rentals_pure(
    rentals: Iterable[Rental],
    *,
    min_days: int,
    discount_tiers: Sequence[tuple[int, float]],
    insurance_rates: Mapping[str, float],
    default_insurance_rate: float,
) -> Report:
    """Відбирає підтверджені прокати та обчислює ціну, знижку і страховку.

    Жодних глобалів: пороги знижки та ставки страхування приходять аргументами.
    Жодних мутацій: кожен запис у результаті - новий словник.
    """
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


# ---------------------------------------------------------------------------
# Завдання 2: параметризація через typing.Callable (фабрика обробника)
# ---------------------------------------------------------------------------


def make_processor(
    *,
    accept: AcceptFn,
    apply_discount: DiscountFn,
    insurance_fee: InsuranceFn,
) -> Processor:
    """Фабрика: повертає налаштований обробник прокатів.

    Усі політики (фільтр, знижка, страхування) - функції, тому будь-яку
    можна замінити, не змінюючи код обробника (компонувальний підхід).
    """

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


# ---- Фабрики політик (функції вищого порядку) -----------------------------


def make_min_days_filter(min_days: int) -> AcceptFn:
    """Приймати лише підтверджені прокати тривалістю не менше ``min_days``."""
    return lambda r: is_confirmed(r) and r["days"] >= min_days


def make_duration_discount(tiers: Sequence[tuple[int, float]]) -> DiscountFn:
    """Знижка за тривалість: повертає ціну ПІСЛЯ знижки."""
    frozen = tuple(tiers)  # власна копія - зовнішній список не впливає
    return lambda r, price: price * (1 - duration_discount_rate(r["days"], frozen))


def make_class_insurance(
    rates: Mapping[str, float], default: float = 0.0
) -> InsuranceFn:
    """Страховий збір як відсоток від ціни залежно від класу авто."""
    frozen = dict(rates)
    return lambda r, price: price * insurance_rate_for(r["car_class"], frozen, default)


def make_per_day_insurance(fee_per_day: float) -> InsuranceFn:
    """Альтернативна політика: фіксований страховий збір за кожен день."""
    return lambda r, _price: r["days"] * fee_per_day


def lift_price_fn(fn: PriceFn) -> DiscountFn:
    """Перетворює просту функцію ``price -> price`` на політику знижки."""
    return lambda _r, price: fn(price)


# ---------------------------------------------------------------------------
# Завдання 3: інжекція залежностей (час) без втрати чистоти
# ---------------------------------------------------------------------------


def stamp_total(total: float, now: NowFn) -> tuple[float, float]:
    """Чиста щодо ``total``: «час» приходить ззовні через ``now``."""
    return total, now()


def stamp_report(report: Report, now: NowFn) -> dict[str, object]:
    """Повертає новий словник звіту з позначкою часу (звіт не змінюється)."""
    return {**report, "generated_at": now()}


# ---------------------------------------------------------------------------
# Додаткові вправи: compose, make_multiplier, без мутацій списків
# ---------------------------------------------------------------------------

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """compose(f, g)(x) == f(g(x))."""
    return lambda x: f(g(x))


def pipe(*fns: PriceFn) -> PriceFn:
    """pipe(f, g, h)(x) == h(g(f(x))) - зліва направо, зручно для знижок."""

    def identity(x: float) -> float:
        return x

    result: PriceFn = identity
    for fn in fns:
        result = compose(fn, result)
    return result


def make_multiplier(k: int) -> Callable[[int], int]:
    """Фабрика множників: make_multiplier(3)(5) == 15."""
    return lambda x: x * k


def make_percent_off(percent: float) -> PriceFn:
    """Знижка у відсотках як функція ціни."""
    return lambda price: price * (1 - percent / 100)


def make_coupon(amount: float) -> PriceFn:
    """Купон на фіксовану суму (ціна не стає від'ємною)."""
    return lambda price: max(0.0, price - amount)


def mark_cancelled(rentals: Sequence[Rental], ids: Iterable[int]) -> list[Rental]:
    """Замість зміни списку «на місці» повертає новий список нових записів."""
    to_cancel = frozenset(ids)
    return [
        {**r, "status": "cancelled"} if r["id"] in to_cancel else r for r in rentals
    ]


def totals_by_class(rentals: Sequence[Rental]) -> dict[str, float]:
    """Сума total за класами авто - новий словник, без накопичувальних мутацій."""
    classes = sorted({r["car_class"] for r in rentals})
    return {
        cls: sum(r["total"] for r in rentals if r["car_class"] == cls)
        for cls in classes
    }

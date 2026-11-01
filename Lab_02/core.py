"""Чисте ядро ЛР2, варіант 9: конвеєр обробки працівників компанії."""

from collections.abc import Callable, Iterable
from functools import reduce
from itertools import islice
from typing import TypedDict


class Employee(TypedDict, total=False):
    """Запис працівника. Поле total_hours з'являється після обробки."""

    id: int
    name: str
    department: str
    monthly_hours: list[float]
    total_hours: float


class Stats(TypedDict):
    """Результат reduce-агрегації."""

    count: int
    total_hours: float
    avg_hours: float


Stage = Callable[[Iterable[Employee]], Iterable[Employee]]


def compose(*funcs: Stage) -> Stage:
    """Композиція справа наліво: compose(f, g)(x) == f(g(x))."""

    def composed(records: Iterable[Employee]) -> Iterable[Employee]:
        """Пропускає записи через усі етапи, починаючи з останнього."""
        return reduce(lambda acc, f: f(acc), reversed(funcs), records)

    return composed


def pipe(*funcs: Stage) -> Stage:
    """Композиція зліва направо: pipe(f, g)(x) == g(f(x))."""
    return compose(*reversed(funcs))


def normalize_names() -> Stage:
    """Приводить імена до вигляду Title Case."""

    def normalize(e: Employee) -> Employee:
        """Повертає новий запис з нормалізованим ім'ям."""
        return {**e, "name": str(e.get("name", "")).strip().title()}

    return lambda recs: map(normalize, recs)


def with_total_hours() -> Stage:
    """Додає поле total_hours як суму відпрацьованих годин за місяці."""

    def add_total(e: Employee) -> Employee:
        """Повертає новий запис із сумою годин."""
        return {**e, "total_hours": float(sum(e.get("monthly_hours", [])))}

    return lambda recs: map(add_total, recs)


def boost_department(department: str, factor: float) -> Stage:
    """Множить total_hours на коефіцієнт для вибраного відділу."""

    def boost(e: Employee) -> Employee:
        """Повертає новий запис з урахуванням коефіцієнта відділу."""
        hours = e.get("total_hours", 0.0)
        if e.get("department") == department:
            return {**e, "total_hours": hours * factor}
        return {**e, "total_hours": hours}

    return lambda recs: map(boost, recs)


def at_least_hours(min_hours: float) -> Stage:
    """Відбирає працівників, у яких total_hours не менше за мінімум."""
    return lambda recs: filter(lambda e: e.get("total_hours", 0.0) >= min_hours, recs)


def sort_by_hours_desc() -> Stage:
    """Сортує за total_hours спадно, при рівності за id зростанням."""
    return lambda recs: sorted(
        recs, key=lambda e: (-e.get("total_hours", 0.0), e.get("id", 0))
    )


def take(n: int) -> Stage:
    """Бере перші n записів."""
    return lambda recs: list(islice(recs, max(n, 0)))


def reduce_stats(records: Iterable[Employee]) -> Stats:
    """Обчислює count, total_hours та avg_hours однією згорткою reduce."""
    count, total = reduce(
        lambda acc, e: (acc[0] + 1, acc[1] + e.get("total_hours", 0.0)),
        records,
        (0, 0.0),
    )
    return {
        "count": count,
        "total_hours": total,
        "avg_hours": total / count if count else 0.0,
    }


def build_pipeline(
    *,
    top_n: int = 3,
    department: str = "IT",
    factor: float = 1.1,
    min_hours: float = 400.0,
) -> Stage:
    """Збирає конвеєр через compose: нормалізація, сума, коефіцієнт, фільтр, Top-N."""
    return compose(
        take(top_n),
        sort_by_hours_desc(),
        at_least_hours(min_hours),
        boost_department(department, factor),
        with_total_hours(),
        normalize_names(),
    )

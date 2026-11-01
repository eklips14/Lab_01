"""Pure-оновлення та бізнес-функції системи доставки (ЛР3, варіант 9)."""

from collections.abc import Iterable, Mapping
from dataclasses import replace
from functools import lru_cache
from types import MappingProxyType

from model import Parcel, RoutePoint, Status, make_meta

ALLOWED_TRANSITIONS: Mapping[Status, frozenset[Status]] = MappingProxyType(
    {
        "created": frozenset({"in_transit", "returned"}),
        "in_transit": frozenset({"delivered", "returned"}),
        "delivered": frozenset(),
        "returned": frozenset(),
    }
)


def add_route_point(parcel: Parcel, city: str, hub: str, hours: float) -> Parcel:
    """Pure update: додає точку маршруту (конкатенація tuple)."""
    return parcel.with_point(RoutePoint(city, hub, hours))


def add_label(parcel: Parcel, label: str) -> Parcel:
    """Pure update: додає мітку (операція frozenset)."""
    return parcel.with_label(label)


def remove_label(parcel: Parcel, label: str) -> Parcel:
    """Pure update: прибирає мітку (різниця frozenset)."""
    return replace(parcel, labels=parcel.labels - frozenset({label}))


def change_status(parcel: Parcel, status: Status) -> Parcel:
    """Pure update: змінює статус, якщо такий перехід дозволено."""
    if status not in ALLOWED_TRANSITIONS[parcel.status]:
        raise ValueError(f"Недозволений перехід: {parcel.status} -> {status}")
    return parcel.with_status(status)


def update_meta(parcel: Parcel, **changes: str) -> Parcel:
    """Pure update: нова read-only мапа метаданих з доданими значеннями."""
    return replace(parcel, meta=make_meta(**{**parcel.meta, **changes}))


@lru_cache(maxsize=None)
def delivery_cost(weight_kg: float, points: int, express: bool) -> float:
    """Вартість доставки: 40 грн + 15 грн/кг + 25 грн за точку, express x1.5."""
    base = 40.0 + 15.0 * weight_kg + 25.0 * points
    return round(base * (1.5 if express else 1.0), 2)


def parcel_cost(parcel: Parcel) -> float:
    """Вартість конкретної посилки (кешований розрахунок)."""
    return delivery_cost(
        parcel.weight_kg, len(parcel.route), "express" in parcel.labels
    )


def freeze(obj: object) -> object:
    """Глибоке заморожування: dict -> proxy, list -> tuple, set -> frozenset."""
    if isinstance(obj, Mapping):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(x) for x in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(x) for x in obj)
    return obj


def index_by_id_and_labels(
    parcels: Iterable[Parcel],
) -> Mapping[tuple[int, frozenset[str]], Parcel]:
    """Індекс посилок за ключем (id, labels) - працює завдяки хешованості."""
    return MappingProxyType({(p.id, p.labels): p for p in parcels})

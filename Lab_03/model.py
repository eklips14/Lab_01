"""Незмінна модель системи доставки (ЛР3, варіант 9)."""

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Literal

Status = Literal["created", "in_transit", "delivered", "returned"]


def make_meta(**kwargs: str) -> Mapping[str, str]:
    """Створює read-only мапу метаданих з копії переданих значень."""
    return MappingProxyType(dict(kwargs))


@dataclass(frozen=True, slots=True)
class RoutePoint:
    """Точка маршруту посилки."""

    city: str
    hub: str
    hours: float


@dataclass(frozen=True, slots=True)
class Parcel:
    """Посилка. Маршрут - tuple, мітки - frozenset, meta - MappingProxyType.

    Поле meta виключено з хешу (hash=False), бо MappingProxyType не хешується.
    """

    id: int
    sender: str
    weight_kg: float
    status: Status = "created"
    route: tuple[RoutePoint, ...] = ()
    labels: frozenset[str] = frozenset()
    meta: Mapping[str, str] = field(default_factory=make_meta, hash=False)

    def total_hours(self) -> float:
        """Сумарний час доставки за маршрутом."""
        return sum(p.hours for p in self.route)

    def with_point(self, point: RoutePoint) -> "Parcel":
        """Повертає нову посилку з доданою точкою маршруту."""
        return replace(self, route=self.route + (point,))

    def with_label(self, label: str) -> "Parcel":
        """Повертає нову посилку з доданою міткою."""
        return replace(self, labels=self.labels | frozenset({label}))

    def with_status(self, status: Status) -> "Parcel":
        """Повертає нову посилку з новим статусом."""
        return replace(self, status=status)

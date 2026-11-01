"""Порівняння часу: мутабельна версія (до) і незмінна (після).

Запуск: python -m pytest --durations=5
"""

from typing import Any

from core import add_label, add_route_point
from model import Parcel

ROUTE_STEPS = 2_000
LABEL_UPDATES = 20_000


def add_point_mutable(parcel: dict[str, Any], city: str, hours: float) -> None:
    """Мутабельна версія «до»: дописує точку маршруту на місці."""
    parcel["route"].append({"city": city, "hub": "Hub", "hours": hours})


def add_label_mutable(parcel: dict[str, Any], label: str) -> None:
    """Мутабельна версія «до»: додає мітку на місці."""
    parcel["labels"].add(label)


def test_before_route_mutable() -> None:
    """До: ROUTE_STEPS in-place додавань точок маршруту."""
    parcel: dict[str, Any] = {"id": 1, "route": [], "labels": set()}
    for i in range(ROUTE_STEPS):
        add_point_mutable(parcel, f"C{i}", 1.0)
    assert len(parcel["route"]) == ROUTE_STEPS


def test_after_route_immutable() -> None:
    """Після: ROUTE_STEPS pure-оновлень, кожне створює новий tuple маршруту."""
    parcel = Parcel(id=1, sender="Shop", weight_kg=1.0)
    for i in range(ROUTE_STEPS):
        parcel = add_route_point(parcel, f"C{i}", "Hub", 1.0)
    assert len(parcel.route) == ROUTE_STEPS


def test_before_labels_mutable() -> None:
    """До: LABEL_UPDATES in-place додавань міток."""
    parcel: dict[str, Any] = {"id": 1, "route": [], "labels": set()}
    for i in range(LABEL_UPDATES):
        add_label_mutable(parcel, f"L{i % 10}")
    assert len(parcel["labels"]) == 10


def test_after_labels_immutable() -> None:
    """Після: LABEL_UPDATES pure-оновлень міток через frozenset."""
    parcel = Parcel(id=1, sender="Shop", weight_kg=1.0)
    for i in range(LABEL_UPDATES):
        parcel = add_label(parcel, f"L{i % 10}")
    assert len(parcel.labels) == 10

"""Тести незмінності моделі доставки (ЛР3, варіант 9)."""

from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from core import (
    add_label,
    add_route_point,
    change_status,
    delivery_cost,
    freeze,
    index_by_id_and_labels,
    parcel_cost,
    remove_label,
    update_meta,
)
from model import Parcel, RoutePoint, make_meta


@pytest.fixture
def parcel() -> Parcel:
    """Базова посилка для тестів."""
    return Parcel(
        id=1,
        sender="Shop",
        weight_kg=2.0,
        route=(RoutePoint("Lviv", "Hub-1", 3.0),),
        labels=frozenset({"fragile"}),
        meta=make_meta(source="web"),
    )


def test_no_mutation_when_adding_point(parcel: Parcel) -> None:
    """Тест: додавання точки маршруту не змінює оригінал."""
    original = parcel
    snapshot = replace(parcel)
    new = add_route_point(parcel, "Kyiv", "Hub-2", 5.0)
    assert parcel is original
    assert parcel == snapshot
    assert new is not parcel
    assert len(new.route) == 2 and len(parcel.route) == 1
    assert new.total_hours() == parcel.total_hours() + 5.0


def test_labels_pure_update(parcel: Parcel) -> None:
    """Тест: мітки додаються і прибираються без мутації."""
    tagged = add_label(parcel, "express")
    assert tagged.labels == frozenset({"fragile", "express"})
    assert parcel.labels == frozenset({"fragile"})
    assert remove_label(tagged, "fragile").labels == frozenset({"express"})


def test_status_transitions(parcel: Parcel) -> None:
    """Тест: зміна статусу і заборонені переходи."""
    moving = change_status(parcel, "in_transit")
    assert moving.status == "in_transit" and parcel.status == "created"
    assert change_status(moving, "delivered").status == "delivered"
    with pytest.raises(ValueError):
        change_status(parcel, "delivered")


def test_frozen_fields(parcel: Parcel) -> None:
    """Тест: поля frozen dataclass змінити не можна."""
    with pytest.raises(FrozenInstanceError):
        parcel.status = "returned"  # type: ignore[misc]


def test_meta_is_read_only(parcel: Parcel) -> None:
    """Тест: meta - read-only MappingProxyType."""
    assert isinstance(parcel.meta, MappingProxyType)
    with pytest.raises(TypeError):
        parcel.meta["source"] = "changed"  # type: ignore[index]


def test_make_meta_copies_source() -> None:
    """Тест: make_meta копіює джерело, тож зміна dict не впливає на proxy."""
    source = {"source": "web"}
    meta = make_meta(**source)
    source["source"] = "changed"
    assert meta["source"] == "web"


def test_update_meta_returns_new_copy(parcel: Parcel) -> None:
    """Тест: update_meta повертає нову посилку з новою мапою."""
    updated = update_meta(parcel, courier="Ivan")
    assert dict(updated.meta) == {"source": "web", "courier": "Ivan"}
    assert dict(parcel.meta) == {"source": "web"}


def test_hashability(parcel: Parcel) -> None:
    """Тест: Parcel і RoutePoint хешуються, працюють як ключі set/dict."""
    parcels = {parcel, add_label(parcel, "express")}
    assert len(parcels) == 2
    assert hash(RoutePoint("Lviv", "Hub-1", 3.0)) == hash(parcel.route[0])
    index = index_by_id_and_labels(parcels)
    assert index[(1, frozenset({"fragile"}))] == parcel


def test_mapping_proxy_is_not_hashable() -> None:
    """Тест: саме MappingProxyType заважає хешуванню, тому meta виключено з hash."""
    with pytest.raises(TypeError):
        hash(make_meta(a="b"))


def test_freeze_deep() -> None:
    """Тест: глибоке заморожування вкладених структур."""
    frozen = freeze({"tags": {"a"}, "points": [1, [2, 3]], "info": {"k": "v"}})
    assert isinstance(frozen, MappingProxyType)
    assert frozen["tags"] == frozenset({"a"})
    assert frozen["points"] == (1, (2, 3))
    assert isinstance(frozen["info"], MappingProxyType)


def test_cost_cached(parcel: Parcel) -> None:
    """Тест: вартість доставки рахується правильно і кешується lru_cache."""
    delivery_cost.cache_clear()
    assert parcel_cost(parcel) == 95.0
    assert parcel_cost(add_label(parcel, "express")) == 142.5
    parcel_cost(parcel)
    assert delivery_cost.cache_info().hits == 1

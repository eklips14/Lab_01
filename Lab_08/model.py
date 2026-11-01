"""ADT JSON-подібного дерева (ЛР8, варіант 9).

JSON = JNull | JBool | JNumber | JString | JArray | JObject - сума варіантів,
кожен вузол - незмінний frozen dataclass. JArray та JObject рекурсивні.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

Kind = Literal["null", "bool", "number", "string", "array", "object"]


@dataclass(frozen=True, slots=True)
class JNull:
    """JSON null."""


@dataclass(frozen=True, slots=True)
class JBool:
    """JSON true/false."""

    value: bool


@dataclass(frozen=True, slots=True)
class JNumber:
    """JSON число."""

    value: int | float


@dataclass(frozen=True, slots=True)
class JString:
    """JSON рядок."""

    value: str


@dataclass(frozen=True, slots=True)
class JArray:
    """JSON масив: незмінний tuple вузлів."""

    items: tuple[JSON, ...] = ()


@dataclass(frozen=True, slots=True)
class JObject:
    """JSON об'єкт: незмінний tuple пар (ключ, вузол) зі збереженням порядку."""

    fields: tuple[tuple[str, JSON], ...] = ()


type JSON = JNull | JBool | JNumber | JString | JArray | JObject


@runtime_checkable
class SupportsToJSON(Protocol):
    """Структурний контракт: будь-який об'єкт з методом to_json()."""

    def to_json(self) -> JSON:
        """Повертає JSON-дерево, що представляє об'єкт."""
        ...

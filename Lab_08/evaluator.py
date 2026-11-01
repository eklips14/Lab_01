"""Чисті операції над JSON-деревом через match/case (ЛР8, варіант 9)."""

from collections import Counter
from functools import reduce
from typing import assert_never

from model import (
    JSON,
    JArray,
    JBool,
    JNull,
    JNumber,
    JObject,
    JString,
    Kind,
    SupportsToJSON,
)


def kind(node: JSON) -> Kind:
    """Тип вузла як Literal."""
    match node:
        case JNull():
            return "null"
        case JBool():
            return "bool"
        case JNumber():
            return "number"
        case JString():
            return "string"
        case JArray():
            return "array"
        case JObject():
            return "object"
        case _:
            assert_never(node)


def children(node: JSON) -> tuple[JSON, ...]:
    """Безпосередні дочірні вузли."""
    match node:
        case JArray(items=items):
            return items
        case JObject(fields=fields):
            return tuple(value for _, value in fields)
        case _:
            return ()


def count_nodes(node: JSON) -> int:
    """Кількість вузлів дерева (рекурсивно)."""
    return 1 + sum(count_nodes(child) for child in children(node))


def depth(node: JSON) -> int:
    """Глибина дерева: лист має глибину 1."""
    return 1 + max((depth(child) for child in children(node)), default=0)


def stats(node: JSON) -> dict[Kind, int]:
    """Кількість вузлів кожного типу."""
    counts = reduce(
        lambda acc, child: acc + Counter(stats(child)),
        children(node),
        Counter({kind(node): 1}),
    )
    return dict(counts)


def to_python(node: JSON) -> object:
    """Перетворює дерево на звичайні Python-значення."""
    match node:
        case JNull():
            return None
        case JBool(value=b):
            return b
        case JNumber(value=n):
            return n
        case JString(value=s):
            return s
        case JArray(items=items):
            return [to_python(item) for item in items]
        case JObject(fields=fields):
            return {key: to_python(value) for key, value in fields}
        case _:
            assert_never(node)


def from_python(value: object) -> JSON:
    """Будує дерево з Python-значення або об'єкта з протоколом SupportsToJSON."""
    match value:
        case None:
            return JNull()
        case bool(b):
            return JBool(b)
        case int(n) | float(n):
            return JNumber(n)
        case str(s):
            return JString(s)
        case list() | tuple():
            return JArray(tuple(from_python(item) for item in value))
        case dict():
            return JObject(tuple(_field(key, item) for key, item in value.items()))
        case SupportsToJSON():
            return value.to_json()
        case _:
            raise TypeError(f"Непідтримуваний тип: {type(value).__name__}")


def _field(key: object, item: object) -> tuple[str, JSON]:
    """Пара ключ-значення для JObject; ключ має бути рядком."""
    match key:
        case str(name):
            return name, from_python(item)
        case _:
            raise TypeError(f"Ключ об'єкта має бути рядком, отримано {key!r}")


def get(node: JSON, *path: str | int) -> JSON | None:
    """Значення за шляхом з ключів та індексів або None."""
    if not path:
        return node
    head, *rest = path
    match node, head:
        case JObject(fields=fields), str(key):
            found = next((v for k, v in fields if k == key), None)
            return None if found is None else get(found, *rest)
        case JArray(items=items), int(index) if -len(items) <= index < len(items):
            return get(items[index], *rest)
        case _:
            return None


def with_field(obj: JObject, key: str, value: JSON) -> JObject:
    """Повертає НОВИЙ об'єкт з доданим або заміненим полем."""
    kept = tuple((k, v) for k, v in obj.fields if k != key)
    if len(kept) == len(obj.fields):
        return JObject((*obj.fields, (key, value)))
    return JObject(tuple((k, value if k == key else v) for k, v in obj.fields))

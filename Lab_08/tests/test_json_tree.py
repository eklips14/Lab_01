"""pytest-тести ЛР8, варіант 9: JSON-подібне дерево."""

import json
from dataclasses import FrozenInstanceError, dataclass

import pytest

from evaluator import (
    count_nodes,
    depth,
    from_python,
    get,
    kind,
    stats,
    to_python,
    with_field,
)
from model import JSON, JArray, JBool, JNull, JNumber, JObject, JString
from pretty import pretty, render, tree

SAMPLE = {
    "name": "Ivan",
    "age": 20,
    "score": 9.5,
    "student": True,
    "car": None,
    "langs": ["uk", "en", {"code": "pl", "level": [1, 2]}],
    "empty": {},
    "nothing": [],
}


@pytest.mark.parametrize(
    ("node", "expected_kind", "text"),
    [
        (JNull(), "null", "null"),
        (JBool(True), "bool", "true"),
        (JBool(False), "bool", "false"),
        (JNumber(42), "number", "42"),
        (JNumber(1.5), "number", "1.5"),
        (JString('Привіт "світ"'), "string", '"Привіт \\"світ\\""'),
        (JArray(), "array", "[]"),
        (JObject(), "object", "{}"),
    ],
)
def test_each_variant(node: JSON, expected_kind: str, text: str) -> None:
    """Тест: кожен варіант ADT має свій kind і рендер."""
    assert kind(node) == expected_kind
    assert render(node) == text
    assert count_nodes(node) == 1


def test_render_matches_json_module() -> None:
    """Тест: рендер вкладеної структури збігається з json.dumps."""
    doc = from_python(SAMPLE)
    assert render(doc) == json.dumps(SAMPLE, separators=(",", ":"), ensure_ascii=False)
    assert pretty(doc) == json.dumps(SAMPLE, indent=2, ensure_ascii=False)


def test_round_trip() -> None:
    """Тест: from_python і to_python взаємно обернені."""
    assert to_python(from_python(SAMPLE)) == SAMPLE


def test_count_depth_stats_nested() -> None:
    """Тест: підрахунок вузлів, глибина і статистика для вкладеного дерева."""
    doc = from_python(SAMPLE)
    assert count_nodes(doc) == 16
    assert depth(doc) == 5
    assert stats(doc) == {
        "object": 3,
        "string": 4,
        "number": 4,
        "bool": 1,
        "null": 1,
        "array": 3,
    }


def test_get_by_path() -> None:
    """Тест: доступ за шляхом і відсутні шляхи."""
    doc = from_python(SAMPLE)
    assert get(doc, "langs", 2, "code") == JString("pl")
    assert get(doc, "langs", -1, "level", 0) == JNumber(1)
    assert get(doc, "langs", 10) is None
    assert get(doc, "missing") is None
    assert get(doc, "age", "x") is None
    assert get(doc) == doc


def test_with_field_is_pure() -> None:
    """Тест: with_field повертає новий об'єкт і не змінює старий."""
    obj = JObject((("a", JNumber(1)),))
    added = with_field(obj, "b", JNull())
    replaced = with_field(added, "a", JString("x"))
    assert obj == JObject((("a", JNumber(1)),))
    assert to_python(added) == {"a": 1, "b": None}
    assert to_python(replaced) == {"a": "x", "b": None}


def test_nodes_are_immutable() -> None:
    """Тест: вузли frozen і хешовані."""
    node = JString("x")
    with pytest.raises(FrozenInstanceError):
        node.value = "y"  # type: ignore[misc]
    assert len({JNumber(1), JNumber(1), JNull()}) == 2


def test_bool_is_not_number() -> None:
    """Тест: True перетворюється на JBool, а не JNumber."""
    assert from_python(True) == JBool(True)
    assert from_python(1) == JNumber(1)


def test_protocol_support() -> None:
    """Тест: будь-який об'єкт з to_json() підходить під SupportsToJSON."""

    @dataclass(frozen=True)
    class Point:
        """Точка з методом to_json."""

        x: int
        y: int

        def to_json(self) -> JSON:
            """JSON-представлення точки."""
            return JArray((JNumber(self.x), JNumber(self.y)))

    assert render(from_python({"p": Point(1, 2)})) == '{"p":[1,2]}'


def test_errors() -> None:
    """Тест: непідтримувані типи і нерядкові ключі."""
    with pytest.raises(TypeError):
        from_python({1, 2})
    with pytest.raises(TypeError):
        from_python({1: "a"})


def test_tree_view() -> None:
    """Тест: текстове дерево з типами вузлів."""
    assert tree(from_python({"a": [1, None]})) == (
        "root: object{1}\n  a: array[2]\n    [0]: 1\n    [1]: null"
    )

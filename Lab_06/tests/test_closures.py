"""Тести замикань і валідаторів."""

import pytest

from closures import (
    Validator,
    in_range,
    is_number,
    is_type,
    make_counter,
    make_logger,
    make_memory_sink,
    non_empty,
    one_of,
    positive,
)


def test_counter_keeps_state() -> None:
    """Тест: лічильник зберігає стан, різні лічильники незалежні."""
    a, b = make_counter(10), make_counter()
    assert [a(), a(), b()] == [11, 12, 1]


def test_logger_with_injected_sink() -> None:
    """Тест: логер пише в ін'єктований sink з префіксом."""
    write, history = make_memory_sink()
    log = make_logger("INFO", write)
    log("ready")
    log("done")
    assert history() == ("[INFO] ready", "[INFO] done")


def test_history_is_snapshot() -> None:
    """Тест: history повертає незмінну копію."""
    write, history = make_memory_sink()
    write("a")
    snapshot = history()
    write("b")
    assert snapshot == ("a",) and history() == ("a", "b")


@pytest.mark.parametrize(
    ("validator", "value", "ok"),
    [
        (in_range(0, 10), 5, True),
        (in_range(0, 10), 0, True),
        (in_range(0, 10), 10.5, False),
        (in_range(0, 10), "5", False),
        (positive(), 0.1, True),
        (positive(), 0, False),
        (positive(), True, False),
        (non_empty(), "x", True),
        (non_empty(), "   ", False),
        (non_empty(), [], False),
        (non_empty(), 5, False),
        (is_type(int, float), 3.5, True),
        (is_type(int), "3", False),
        (one_of("a", "b"), "b", True),
        (one_of("a", "b"), "c", False),
        (is_number(), 7, True),
        (is_number(), False, False),
    ],
)
def test_validators(validator: Validator, value: object, ok: bool) -> None:
    """Тест: граничні та некоректні значення для кожного валідатора."""
    assert (validator(value) is None) is ok

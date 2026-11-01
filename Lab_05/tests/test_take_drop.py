"""Тести take/drop."""

from itertools import count, islice

import pytest

from streams import after_non_positive, below, drop, take


def test_take_drop_on_count() -> None:
    """Тест: take просуває спільний ітератор."""
    xs = count(1)
    assert take(5, xs) == [1, 2, 3, 4, 5]
    assert take(3, xs) == [6, 7, 8]


def test_drop_then_take() -> None:
    """Тест: drop пропускає перші n."""
    assert list(islice(drop(10, count(0)), 3)) == [10, 11, 12]


def test_edge_cases() -> None:
    """Тест: n=0, порожнє джерело, від'ємні n."""
    assert take(0, count()) == []
    assert take(5, []) == []
    assert list(drop(3, [1, 2])) == []
    with pytest.raises(ValueError):
        take(-1, [1])
    with pytest.raises(ValueError):
        drop(-1, [1])


def test_takewhile_dropwhile() -> None:
    """Тест: умовні аналоги take/drop."""
    assert list(below(5, count(1))) == [1, 2, 3, 4]
    assert list(after_non_positive([-1, 0, 2, -3, 4])) == [2, -3, 4]

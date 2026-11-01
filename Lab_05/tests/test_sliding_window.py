"""Тести sliding_window, moving_average та chunked."""

from collections.abc import Iterator
from itertools import count, starmap

import pytest

from streams import chunked, moving_average, sliding_window, take


def test_windows_basic() -> None:
    """Тест: базові вікна."""
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]


def test_window_sums() -> None:
    """Тест: суми по вікнах через starmap."""
    sums = list(starmap(lambda a, b: a + b, sliding_window(range(5), 2)))
    assert sums == [1, 3, 5, 7]


def test_window_larger_than_source() -> None:
    """Тест: k більше за довжину - жодного вікна."""
    assert list(sliding_window([1, 2], 3)) == []
    assert list(sliding_window([], 1)) == []


def test_invalid_window() -> None:
    """Тест: некоректний розмір вікна."""
    with pytest.raises(ValueError):
        sliding_window([1, 2], 0)
    with pytest.raises(ValueError):
        chunked([1, 2], -1)


def test_moving_average() -> None:
    """Тест: рухоме середнє на нескінченному потоці."""
    assert take(3, moving_average(count(1), 2)) == [1.5, 2.5, 3.5]


def test_chunked() -> None:
    """Тест: пакети фіксованого розміру."""
    assert list(chunked(range(7), 3)) == [(0, 1, 2), (3, 4, 5), (6,)]


def test_window_laziness() -> None:
    """Тест: для одного вікна береться рівно k елементів."""
    pulled = []

    def numbers() -> Iterator[int]:
        """Нескінченне джерело, що рахує звернення."""
        for n in count():
            pulled.append(n)
            yield n

    assert take(1, sliding_window(numbers(), 4)) == [(0, 1, 2, 3)]
    assert pulled == [0, 1, 2, 3]

"""Тести quicksort."""

import random

from algorithms import quicksort


def test_quicksort_basic() -> None:
    """Тест: базові та граничні випадки."""
    assert quicksort([]) == []
    assert quicksort([1]) == [1]
    assert quicksort([3, 2, 1]) == [1, 2, 3]
    assert quicksort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


def test_quicksort_random() -> None:
    """Тест: збіг із sorted на випадкових даних."""
    xs = [random.randint(-1000, 1000) for _ in range(1000)]
    assert quicksort(xs) == sorted(xs)


def test_quicksort_does_not_mutate() -> None:
    """Тест: вхідний список не змінюється."""
    xs = [5, 1, 4]
    quicksort(xs)
    assert xs == [5, 1, 4]

"""Тести Фібоначчі та хвостової рекурсії."""

import pytest

from algorithms import fact, fib, fib_iter, fib_naive


def test_fib_small() -> None:
    """Тест: перші 10 значень."""
    assert [fib(i) for i in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_fib_iter_matches() -> None:
    """Тест: мемоізована, наївна та ітеративна версії збігаються."""
    for n in range(50):
        assert fib(n) == fib_iter(n)
    assert fib_naive(15) == fib(15)


def test_cache_clear_and_info() -> None:
    """Тест: API кешу lru_cache."""
    fib.cache_clear()
    fib(30)
    assert fib.cache_info().currsize == 31
    fib(30)
    assert fib.cache_info().hits >= 1
    fib.cache_clear()
    assert fib.cache_info().currsize == 0


def test_negative_input() -> None:
    """Тест: від'ємний аргумент - ValueError."""
    with pytest.raises(ValueError):
        fib(-1)
    with pytest.raises(ValueError):
        fib_iter(-1)


def test_fact_tail_recursion() -> None:
    """Тест: факторіал і відсутність TCO на великій глибині."""
    assert fact(5) == 120
    assert fact(0) == 1
    with pytest.raises(RecursionError):
        fact(100_000)

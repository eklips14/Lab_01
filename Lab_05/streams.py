"""Базові ліниві утиліти ЛР5: Фібоначчі, take/drop, sliding window, accumulate."""

import operator
from collections import deque
from collections.abc import Iterable, Iterator
from itertools import accumulate, count, dropwhile, islice, takewhile


def fib_stream() -> Iterator[int]:
    """Нескінченний потік чисел Фібоначчі."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def naturals(start: int = 1) -> Iterator[int]:
    """Нескінченний лічильник натуральних чисел."""
    yield from count(start)


def take[T](n: int, it: Iterable[T]) -> list[T]:
    """Бере перші n елементів (матеріалізує лише їх)."""
    if n < 0:
        raise ValueError("n має бути невід'ємним")
    return list(islice(it, n))


def drop[T](n: int, it: Iterable[T]) -> Iterator[T]:
    """Пропускає перші n елементів і повертає ітератор на решту."""
    if n < 0:
        raise ValueError("n має бути невід'ємним")
    iterator = iter(it)
    next(islice(iterator, n, n), None)
    return iterator


def sliding_window[T](it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Ліниві ковзні вікна довжини k через deque(maxlen=k)."""
    if k <= 0:
        raise ValueError("Розмір вікна має бути додатним")
    return _windows(iter(it), k)


def _windows[T](iterator: Iterator[T], k: int) -> Iterator[tuple[T, ...]]:
    """Генератор вікон: спершу наповнює вікно, далі зсуває по одному."""
    window: deque[T] = deque(islice(iterator, k), maxlen=k)
    if len(window) < k:
        return
    yield tuple(window)
    for x in iterator:
        window.append(x)
        yield tuple(window)


def moving_average(it: Iterable[float], k: int) -> Iterator[float]:
    """Рухоме середнє по вікнах довжини k."""
    return (sum(w) / k for w in sliding_window(it, k))


def chunked[T](it: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Ліниві пакети фіксованого розміру (останній може бути коротшим)."""
    if k <= 0:
        raise ValueError("Розмір пакета має бути додатним")
    return _chunks(iter(it), k)


def _chunks[T](iterator: Iterator[T], k: int) -> Iterator[tuple[T, ...]]:
    """Генератор пакетів через islice."""
    while chunk := tuple(islice(iterator, k)):
        yield chunk


def prefix_sums(xs: Iterable[float]) -> Iterator[float]:
    """Префіксні суми через accumulate."""
    return accumulate(xs)


def prefix_products(xs: Iterable[int]) -> Iterator[int]:
    """Префіксні добутки через accumulate з operator.mul."""
    return accumulate(xs, operator.mul)


def below(limit: float, it: Iterable[float]) -> Iterator[float]:
    """Бере значення, поки вони менші за поріг (takewhile)."""
    return takewhile(lambda x: x < limit, it)


def after_non_positive(it: Iterable[float]) -> Iterator[float]:
    """Пропускає початкові недодатні значення (dropwhile)."""
    return dropwhile(lambda x: x <= 0, it)

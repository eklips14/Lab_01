"""Тести потоку Фібоначчі."""

from itertools import islice

from streams import drop, fib_stream, take


def test_first_10() -> None:
    """Тест: перші 10 значень."""
    assert list(islice(fib_stream(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_drop_then_take_fib() -> None:
    """Тест: пропустити 5, взяти 8."""
    assert take(8, drop(5, fib_stream())) == [5, 8, 13, 21, 34, 55, 89, 144]

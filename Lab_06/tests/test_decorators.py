"""Тести декораторів @validate, @timed, @count_calls та їх композиції."""

import inspect
from collections.abc import Callable

import pytest

from closures import in_range, is_type, make_counter, make_memory_sink, non_empty
from decorators import ValidationError, count_calls, timed, validate


def fake_clock(*ticks: float) -> Callable[[], float]:
    """Детермінований годинник, що повертає задані значення по черзі."""
    values = iter(ticks)
    return lambda: next(values)


def test_validate_accepts_valid_arguments() -> None:
    """Тест: коректні аргументи проходять."""

    @validate(x=in_range(0, 10))
    def double(x: int) -> int:
        """Подвоює число."""
        return x * 2

    assert double(4) == 8
    assert double(x=10) == 20


def test_validate_rejects_and_collects_errors() -> None:
    """Тест: усі помилки збираються в одне повідомлення."""

    @validate(name=[is_type(str), non_empty()], age=in_range(0, 120))
    def make(name: str, age: int) -> str:
        """Створює опис."""
        return f"{name}:{age}"

    with pytest.raises(ValidationError) as info:
        make("", 200)
    message = str(info.value)
    assert "name: не може бути порожнім" in message
    assert "age: має бути в межах" in message


def test_validate_checks_default_values() -> None:
    """Тест: значення за замовчуванням теж перевіряються."""

    @validate(limit=in_range(1, 5))
    def fetch(limit: int = 10) -> int:
        """Повертає ліміт."""
        return limit

    with pytest.raises(ValidationError):
        fetch()
    assert fetch(3) == 3


def test_validate_unknown_parameter() -> None:
    """Тест: правило для неіснуючого параметра - TypeError при декоруванні."""
    with pytest.raises(TypeError):

        @validate(missing=non_empty())
        def f(x: int) -> int:
            """Нічого не робить."""
            return x


def test_validate_does_not_call_function_on_error() -> None:
    """Тест: при помилці валідації функція не викликається."""
    calls = make_counter()

    @validate(x=in_range(0, 1))
    def f(x: int) -> int:
        """Рахує виклики."""
        return calls()

    with pytest.raises(ValidationError):
        f(5)
    assert f(1) == 1


def test_timed_uses_clock_and_logger() -> None:
    """Тест: таймінг без реального часу."""
    write, history = make_memory_sink()

    @timed("work", unit="ms", logger=write, clock=fake_clock(0.0, 0.012345))
    def work(x: int) -> int:
        """Квадрат числа."""
        return x * x

    assert work(5) == 25
    assert history() == ("[timed] work took 12.345 ms",)


def test_timed_logs_on_exception() -> None:
    """Тест: час логується навіть якщо функція кинула виняток."""
    write, history = make_memory_sink()

    @timed(unit="s", logger=write, clock=fake_clock(1.0, 3.5))
    def boom() -> None:
        """Завжди падає."""
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        boom()
    assert history() == ("[timed] boom took 2.500 s",)


def test_count_calls_state() -> None:
    """Тест: кожна функція має власний лічильник у замиканні."""
    write, history = make_memory_sink()

    @count_calls(logger=write)
    def a() -> None:
        """Функція a."""

    @count_calls(logger=write)
    def b() -> None:
        """Функція b."""

    a()
    a()
    b()
    assert history() == (
        "[count_calls] a call #1",
        "[count_calls] a call #2",
        "[count_calls] b call #1",
    )


def test_count_calls_injected_counter() -> None:
    """Тест: фабрика лічильника передається як залежність."""
    write, history = make_memory_sink()

    @count_calls(logger=write, counter_factory=lambda: make_counter(100))
    def f() -> None:
        """Функція f."""

    f()
    assert history() == ("[count_calls] f call #101",)


@pytest.mark.parametrize(
    "decorator",
    [
        validate(x=in_range(0, 10)),
        timed(logger=lambda _: None),
        count_calls(logger=lambda _: None),
    ],
)
def test_wraps_preserves_metadata(
    decorator: Callable[[Callable[[int], int]], Callable[[int], int]],
) -> None:
    """Тест: __name__, __doc__ і __wrapped__ збережено."""

    def original(x: int) -> int:
        """Оригінальний докстрінг."""
        return x

    wrapped = decorator(original)
    assert wrapped.__name__ == "original"
    assert wrapped.__doc__ == "Оригінальний докстрінг."
    assert inspect.unwrap(wrapped) is original


def test_decorator_order_matters() -> None:
    """Тест: порядок композиції змінює, чи рахуються невалідні виклики."""
    write_outer, outer_log = make_memory_sink()
    write_inner, inner_log = make_memory_sink()

    @count_calls(logger=write_outer)
    @validate(x=in_range(0, 1))
    def counted_first(x: int) -> int:
        """Лічильник зовні: рахує і невалідні виклики."""
        return x

    @validate(x=in_range(0, 1))
    @count_calls(logger=write_inner)
    def validated_first(x: int) -> int:
        """Валідація зовні: невалідні виклики не доходять до лічильника."""
        return x

    for f in (counted_first, validated_first):
        with pytest.raises(ValidationError):
            f(5)
        f(1)
    assert len(outer_log()) == 2
    assert len(inner_log()) == 1

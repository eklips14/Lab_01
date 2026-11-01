"""Параметризовані декоратори ЛР6, варіант 9: @validate, @timed, @count_calls."""

import functools
import inspect
import time
from collections.abc import Callable, Sequence
from typing import Literal, ParamSpec, TypeVar

from closures import Validator, make_counter

P = ParamSpec("P")
R = TypeVar("R")


class ValidationError(ValueError):
    """Аргументи функції не пройшли валідацію."""


def validate(
    **rules: Validator | Sequence[Validator],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Фабрика декоратора: перевіряє аргументи до виклику функції.

    Приклад: @validate(age=in_range(0, 120), name=[non_empty(), is_type(str)]).
    """
    checks = {
        name: tuple(rule) if isinstance(rule, Sequence) else (rule,)
        for name, rule in rules.items()
    }

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Звичайний декоратор із захопленими правилами."""
        signature = inspect.signature(func)
        unknown = set(checks) - set(signature.parameters)
        if unknown:
            raise TypeError(f"{func.__name__} не має параметрів {sorted(unknown)}")

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Перевіряє аргументи і викликає оригінальну функцію."""
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            errors = [
                f"{name}: {message}"
                for name, validators in checks.items()
                for check in validators
                if (message := check(bound.arguments[name])) is not None
            ]
            if errors:
                raise ValidationError(f"{func.__name__}: " + "; ".join(errors))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def timed(
    label: str | None = None,
    *,
    unit: Literal["s", "ms", "us"] = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Фабрика декоратора: логує час виконання (навіть при винятку)."""
    factor = {"s": 1.0, "ms": 1e3, "us": 1e6}[unit]

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Звичайний декоратор із захопленими налаштуваннями."""
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Вимірює час виклику через ін'єктований clock."""
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                logger(f"[timed] {name} took {(clock() - start) * factor:.3f} {unit}")

        return wrapper

    return decorator


def count_calls(
    *,
    logger: Callable[[str], None] = print,
    counter_factory: Callable[[], Callable[[], int]] = make_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Фабрика декоратора: рахує виклики через замикання-лічильник."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        """Кожна задекорована функція отримує власний лічильник."""
        counter = counter_factory()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            """Збільшує лічильник і викликає функцію."""
            logger(f"[count_calls] {func.__name__} call #{counter()}")
            return func(*args, **kwargs)

        return wrapper

    return decorator

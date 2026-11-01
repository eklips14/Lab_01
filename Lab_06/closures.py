"""Замикання ЛР6, варіант 9: лічильник, логер і фабрика валідаторів."""

from collections.abc import Callable
from numbers import Real

Validator = Callable[[object], str | None]
"""Валідатор повертає текст помилки або None, якщо значення коректне."""


def make_counter(start: int = 0) -> Callable[[], int]:
    """Лічильник викликів: стан value зберігається в замиканні через nonlocal."""
    value = start

    def inc() -> int:
        """Збільшує лічильник і повертає нове значення."""
        nonlocal value
        value += 1
        return value

    return inc


def make_logger(prefix: str, sink: Callable[[str], None]) -> Callable[[str], None]:
    """Логер з префіксом; куди писати (sink) передається як залежність."""

    def log(message: str) -> None:
        """Пише повідомлення з префіксом."""
        sink(f"[{prefix}] {message}")

    return log


def make_memory_sink() -> tuple[Callable[[str], None], Callable[[], tuple[str, ...]]]:
    """Пара замикань: запис повідомлень і читання накопиченої історії."""
    messages: list[str] = []

    def write(message: str) -> None:
        """Зберігає повідомлення."""
        messages.append(message)

    def history() -> tuple[str, ...]:
        """Повертає незмінну копію історії."""
        return tuple(messages)

    return write, history


def is_number() -> Validator:
    """Значення має бути числом (але не bool)."""
    return lambda x: (
        None if isinstance(x, Real) and not isinstance(x, bool) else "має бути числом"
    )


def in_range(lo: float, hi: float) -> Validator:
    """Число в межах [lo, hi]; межі захоплені замиканням."""

    def check(x: object) -> str | None:
        """Перевіряє діапазон."""
        if not isinstance(x, Real) or isinstance(x, bool):
            return "має бути числом"
        return None if lo <= float(x) <= hi else f"має бути в межах [{lo}, {hi}]"

    return check


def positive() -> Validator:
    """Число більше нуля."""

    def check(x: object) -> str | None:
        """Перевіряє, що число додатне."""
        if not isinstance(x, Real) or isinstance(x, bool):
            return "має бути числом"
        return None if float(x) > 0 else "має бути додатним"

    return check


def non_empty() -> Validator:
    """Рядок або колекція не порожні."""

    def check(x: object) -> str | None:
        """Перевіряє непорожність."""
        if isinstance(x, str):
            return None if x.strip() else "не може бути порожнім"
        if isinstance(x, (list, tuple, set, frozenset, dict)):
            return None if x else "не може бути порожнім"
        return "має бути рядком або колекцією"

    return check


def is_type(*types: type) -> Validator:
    """Значення має один із дозволених типів."""
    names = ", ".join(t.__name__ for t in types)
    return lambda x: None if isinstance(x, types) else f"має бути типу {names}"


def one_of(*options: object) -> Validator:
    """Значення входить до дозволеного набору."""
    allowed = tuple(options)
    return lambda x: None if x in allowed else f"має бути одним із {allowed}"

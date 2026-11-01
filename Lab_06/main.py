"""Точка входу лабораторної роботи №6, варіант 9."""

from closures import in_range, is_type, make_logger, non_empty, one_of, positive
from decorators import ValidationError, count_calls, timed, validate

log = make_logger("APP", print)


@timed("register", unit="us", logger=log)
@count_calls(logger=log)
@validate(
    name=[is_type(str), non_empty()],
    age=in_range(18, 65),
    salary=positive(),
    role=one_of("dev", "qa", "pm"),
)
def register_employee(name: str, age: int, salary: float, role: str = "dev") -> str:
    """Реєструє працівника і повертає опис запису."""
    return f"{name.strip().title()} ({role}), {age} р., {salary:.2f} грн"


def run() -> None:
    """Демонструє валідацію, таймінг і лічильник викликів."""
    print(register_employee("ivan petrenko", 30, 25000))
    print(register_employee("olena", 41, 31000, role="pm"))
    for args in [("", 17, -5.0, "ceo"), ("Petro", 70, 1000.0, "qa")]:
        try:
            register_employee(*args)
        except ValidationError as error:
            print(f"Помилка валідації: {error}")
    print(f"Метадані збережено: {register_employee.__name__}")
    print(f"Докстрінг: {register_employee.__doc__}")


def main() -> None:
    """Запуск демонстрації декораторів."""
    run()


if __name__ == "__main__":
    main()

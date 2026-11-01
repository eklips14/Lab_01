"""Точка входу лабораторної роботи №5, варіант 9."""

from itertools import islice

from schedule import cumulative_hours, days_until, duty_roster, plan, weeks
from streams import drop, fib_stream, moving_average, naturals, sliding_window, take

SHIFTS = ("Ранок", "День", "Ніч", "Вихідний")
HOURS = {"Ранок": 8.0, "День": 8.0, "Ніч": 10.0, "Вихідний": 0.0}
WORKERS = ("Іван", "Олена", "Петро")


def run() -> None:
    """Демонструє лінивий циклічний розклад і базові потоки."""
    print("План на 10 днів (старт у середу):")
    for day in plan(SHIFTS, 10, start_weekday=2):
        print(f"  день {day.number:>2} ({day.weekday}): {day.shift}")

    print("\nГрафік чергувань на 6 днів:")
    for duty in islice(duty_roster(WORKERS, SHIFTS), 6):
        print(f"  день {duty.number}: {duty.worker} - {duty.shift}")

    print(f"\nДнів до першої нічної зміни: {len(days_until(SHIFTS, 'Ніч'))}")
    print(f"Накопичені години за 8 днів: {cumulative_hours(SHIFTS, HOURS, 8)}")
    first_week = weeks(SHIFTS, 1)[0]
    print(f"Перший тиждень: {[d.shift for d in first_week]}")

    print("\nБазові потоки:")
    print(f"  перші 10 Фібоначчі: {take(10, fib_stream())}")
    print(f"  пропустити 5, взяти 8: {take(8, drop(5, fib_stream()))}")
    print(f"  вікна по 3: {take(3, sliding_window(naturals(), 3))}")
    print(f"  рухоме середнє k=2: {take(4, moving_average(naturals(), 2))}")


def main() -> None:
    """Запуск демонстрації лінивого розкладу."""
    run()


if __name__ == "__main__":
    main()

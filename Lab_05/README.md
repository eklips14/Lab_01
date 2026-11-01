# Лабораторна робота №5 (Варіант 9 - Циклічний розклад)

## Опис
Ліниві обчислення: генератори та `itertools`.

**Варіант 9 (`schedule.py`).** Нескінченний циклічний розклад змін. Значення обчислюються лише в міру запиту, нескінченні потоки завжди обмежуються `take`/`islice`/`takewhile`.

- `cyclic_schedule(shifts, start_weekday)` - нескінченний потік днів: нумерація `count`, дні тижня і зміни через `cycle`, об'єднання через `zip`;
- `plan(shifts, days)` - план на N днів (`islice`);
- `duty_roster(workers, shifts)` - графік чергувань, де працівники і зміни чергуються незалежно;
- `days_until(shifts, target)` - дні до першої потрібної зміни (`takewhile`);
- `weeks(shifts, n)` - розклад по тижнях (ліниві пакети `chunked`);
- `cumulative_hours(shifts, hours, days)` - накопичені години (`accumulate`).

**Базова частина (`streams.py`).** `fib_stream`, `naturals`, `take`, `drop`, `sliding_window` (через `deque(maxlen=k)`), `moving_average`, `chunked`, обгортки над `accumulate`, `takewhile`, `dropwhile`.

Тести перевіряють лінивість: з джерела береться рівно стільки елементів, скільки запитано. Також перевірено крайні випадки: порожнє джерело, `n=0`, `k` більше за довжину потоку, некоректний розмір вікна.

## Структура проєкту
```text
Lab_05/
├── main.py
├── schedule.py
├── streams.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── .gitignore
├── tests/
│   ├── test_schedule.py
│   ├── test_fib_stream.py
│   ├── test_take_drop.py
│   ├── test_sliding_window.py
│   └── test_accumulate.py
└── report/
    └── Obykhod_Ivan_FeP-22_V9.pdf
```

## Як запустити програму
```bash
pip install -r requirements.txt
python main.py
```

## Запуск тестів
```bash
python -m pytest -v
```

## Інструменти перевірки якості коду
```bash
mypy .
black --check .
ruff check .
```

## Автор
Обиход Іван Віталійович, група ФЕП-22с

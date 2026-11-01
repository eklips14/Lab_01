# Лабораторна робота №6 (Варіант 9 - Декоратор валідації аргументів)

## Опис
Замикання та декоратори як функції вищого порядку.

**Замикання (`closures.py`):**
- `make_counter(start)` - лічильник зі змінним станом через `nonlocal`;
- `make_logger(prefix, sink)` - логер, куди писати передається як залежність;
- `make_memory_sink()` - пара замикань для запису та читання історії (фейковий логер для тестів);
- фабрика валідаторів-замикань: `in_range(lo, hi)`, `positive()`, `non_empty()`, `is_type(*types)`, `one_of(*options)`, `is_number()`.

**Параметризовані декоратори (`decorators.py`):**
- `@validate(**rules)` - перевіряє аргументи до виклику за допомогою `inspect.signature`, враховує значення за замовчуванням і збирає всі помилки у `ValidationError`;
- `@timed(label, unit, logger, clock)` - час виконання з ін'єктованими годинником і логером, лог пишеться навіть при винятку;
- `@count_calls(logger, counter_factory)` - лічильник викликів на основі замикання `make_counter`.

Усі декоратори використовують `functools.wraps`, а типи зберігаються через `ParamSpec` і `TypeVar`. Тести перевіряють `__name__`, `__doc__` і `__wrapped__`, працюють без реального часу і показують, як порядок композиції декораторів змінює поведінку.

## Структура проєкту
```text
Lab_06/
├── main.py
├── closures.py
├── decorators.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── .gitignore
├── tests/
│   ├── test_closures.py
│   └── test_decorators.py
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

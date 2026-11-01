# Лабораторна робота №7 (Варіант 9 - Фільми та рейтинги)

## Опис
`functools` та `operator`: `partial`, `reduce`, `singledispatch`, `total_ordering`, `itemgetter`, `attrgetter`, `methodcaller`.

Вхідні дані: фільми з полями `title`, `genre`, `year`, `rating`, `votes`.

**Конвеєр (`core.py`).** `pipeline(value, *funcs)` реалізовано через `functools.reduce`. Функція `clean_and_rank(src, top, min_year, min_rating, genre)`:
1. завантажує дані через `load_movies`;
2. нормалізує записи (`itemgetter` + `methodcaller("strip")`, `methodcaller("title")`, приведення типів);
3. фільтрує за роком і мінімальним рейтингом (`filter` + `partial(year_at_least, ...)`, `partial(rating_at_least, ...)`), опційно за жанром;
4. сортує за `rating` спадно, `votes` спадно, `title` зростанням (стабільне сортування з `itemgetter`);
5. повертає Top-N.

Додатково: `total_votes` через `reduce(add, ...)`, `best_by_genre` через `reduce` і порівняння `Movie`, `titles` через `attrgetter`.

**Поліморфний API (`loaders.py`).** `load_movies` на `@singledispatch` приймає JSON-рядок, шлях `str` або `pathlib.Path` до `.json`/`.csv`, відкритий текстовий файл (JSON або CSV) і готовий список словників.

**Порівняння (`models.py`).** Клас `Movie` з `@total_ordering`: реалізовано `__eq__` і `__lt__` за ключем (`rating`, `votes`, `title`), для чужих типів повертається `NotImplemented`.

## Структура проєкту
```text
Lab_07/
├── main.py
├── core.py
├── loaders.py
├── models.py
├── sample_data.json
├── sample_data.csv
├── README.md
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── tests/
│   └── test_lab07.py
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

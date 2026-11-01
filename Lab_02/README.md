# Лабораторна робота №2 (Варіант 9 - Працівники компанії)

## Опис
Функції вищого порядку, lambda та композиція. Програма будує конвеєр перетворень над списком працівників без мутації вхідних даних.

Структура запису: `id`, `name`, `department`, `monthly_hours`.

Конвеєр (`build_pipeline`, зібраний через `compose`):
1. нормалізувати імена (`map`);
2. обчислити сумарні години `total_hours` (`map`);
3. застосувати коефіцієнт для вибраного відділу (`map`);
4. відфільтрувати працівників за мінімумом годин (`filter` + `lambda`);
5. відсортувати за `total_hours` спадно, при рівності за `id` (`sorted` з двома ключами);
6. взяти Top-N (`itertools.islice`).

Агрегація через `functools.reduce`: `count`, `total_hours`, `avg_hours`.

- `core.py` - чисті трансформації, `compose`, `pipe`, `reduce_stats`.
- `app.py` - I/O та CLI (`argparse`), функція `run()`.
- `main.py` - точка входу програми.
- `tests/test_core.py` - тести Top-N, відсутності мутацій, агрегації та композиції.

## Структура проєкту
```text
Lab_02/
├── main.py
├── core.py
├── app.py
├── README.md
├── requirements.txt
├── tests/
│   └── test_core.py
└── report/
    └── Obykhod_Ivan_FeP-22_V9.pdf
```

## Як запустити програму
```bash
pip install -r requirements.txt
python main.py
python app.py --top 2 --boost-dept Sales --factor 1.2 --min-hours 300
```

## Запуск тестів
```bash
python -m pytest -v
```

## Інструменти перевірки якості коду
```bash
mypy --strict core.py app.py main.py tests/test_core.py
black --check .
ruff check .
```

## Автор
Обиход Іван Віталійович, група ФЕП-22с

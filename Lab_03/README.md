# Лабораторна робота №3 (Варіант 9 - Система доставки)

## Опис
Незмінні структури даних (immutability). Мутабельну модель посилки перетворено на незмінну:

- `RoutePoint` і `Parcel` - `@dataclass(frozen=True, slots=True)`;
- маршрут `route` - `tuple[RoutePoint, ...]` замість `list`;
- мітки `labels` - `frozenset[str]` замість `set`;
- метадані `meta` - `MappingProxyType` (read-only) з копією джерела (`make_meta`);
- статус обмежено `Literal["created", "in_transit", "delivered", "returned"]`.

Pure-оновлення (`core.py`) повертають нові об'єкти через `dataclasses.replace`, конкатенацію tuple та операції frozenset:
`add_route_point`, `add_label`, `remove_label`, `change_status` (з перевіркою дозволених переходів), `update_meta`.

Просунуті завдання: `freeze(obj)` для глибокого заморожування, кешування вартості доставки через `functools.lru_cache`, індекс посилок за ключем `(id, labels)`.

**Хешованість.** `RoutePoint` і `Parcel` хешуються. `MappingProxyType` не хешується, тому поле `meta` виключено з хешу (`field(hash=False)`). Це перевірено тестами.

## Структура проєкту
```text
Lab_03/
├── main.py
├── model.py
├── core.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── tests/
│   ├── test_immutability.py
│   └── test_performance.py
└── report/
    └── Obykhod_Ivan_FeP-22_V9.pdf
```

## Як запустити програму
```bash
pip install -r requirements.txt
python main.py
```

## Запуск тестів і вимірювання часу
```bash
python -m pytest -v
python -m pytest --durations=5
```

Результат `pytest --durations=0 --durations-min=0 tests/test_performance.py`:

| Тест | Операцій | Час |
|---|---|---|
| до: маршрут, `list.append` | 2 000 | 0.00 s |
| після: маршрут, нова копія `tuple` | 2 000 | 0.01 s |
| до: мітки, `set.add` | 20 000 | 0.01 s |
| після: мітки, нова копія `frozenset` + `replace` | 20 000 | 0.08 s |

## Інструменти перевірки якості коду
```bash
mypy .
black --check .
ruff check .
```

## Висновок
Незмінні структури дають референтну прозорість, хешованість (посилки можна класти в `set` і використовувати як ключі `dict`) та захист від випадкових змін: спроба змінити поле чи `meta` викликає виняток. Накладні витрати - створення нової копії при кожному оновленні: на 20 000 оновлень це десятки мілісекунд, а накопичення маршруту через конкатенацію tuple має квадратичну складність. Для навчальних і більшості прикладних обсягів ця ціна несуттєва.

## Автор
Обиход Іван Віталійович, група ФЕП-22с

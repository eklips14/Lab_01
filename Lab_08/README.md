# Лабораторна робота №8 (Варіант 9 - JSON-подібне дерево)

## Опис
Алгебраїчні типи даних «по-Python'івськи»: `Union`/`TypeAlias`, `Literal`, `Protocol`, структурний pattern matching `match/case`.

**Модель (`model.py`).** ADT як сума варіантів, кожен вузол - `@dataclass(frozen=True, slots=True)`:

```python
type JSON = JNull | JBool | JNumber | JString | JArray | JObject
```

`JArray` і `JObject` рекурсивні: містять `tuple` вузлів `JSON`. Тип вузла описано через `Kind = Literal["null", "bool", "number", "string", "array", "object"]`. Структурний контракт `SupportsToJSON` (`Protocol`) дозволяє перетворити на дерево будь-який об'єкт із методом `to_json()`.

**Операції (`evaluator.py`).** Чисті функції з `match/case` без ланцюгів `if/elif`:
`kind`, `count_nodes`, `depth`, `stats` (кількість вузлів кожного типу), `to_python`, `from_python`, `get` (доступ за шляхом), `with_field` (pure update, повертає новий `JObject`).

**Рендер (`pretty.py`).** `render` (компактний JSON), `pretty` (з відступами), `tree` (структура з типами вузлів). Тести перевіряють, що `render` і `pretty` збігаються з `json.dumps`.

Код проходить `mypy --strict` без помилок, вичерпність `match` контролює `assert_never`.

## Приклад
```text
root: object{2}
  name: "Ivan"
  langs: array[2]
    [0]: "uk"
    [1]: "en"
```

## Структура проєкту
```text
Lab_08/
├── main.py
├── model.py
├── evaluator.py
├── pretty.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── mypy.ini
├── tests/
│   └── test_json_tree.py
└── report/
    └── Obykhod_Ivan_FeP-22_V9.pdf
```

## Як запустити програму
```bash
pip install -r requirements.txt
python main.py
```

## Запуск тестів і перевірки типів
```bash
python -m pytest -v
mypy --strict .
black --check .
ruff check .
```

## Автор
Обиход Іван Віталійович, група ФЕП-22с

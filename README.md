# Лабораторна робота №1. Основи функціонального програмування у Python

**Варіант 9 - Прокат автомобілів**

| Вхідні дані | Основне завдання | Функціональні вимоги |
|---|---|---|
| Клас авто, дні, денна ставка, статус | Обчислити базову ціну, знижку за тривалість і страховий збір | Політики знижки та страхування - функції (`typing.Callable`) |

## Що зроблено

1. **Завдання 1 - переписано імперативний код у функціональному стилі.**
   Стартовий фрагмент із глобалами, `print` у циклі та мутацією вхідних словників
   збережено для порівняння у `starter_imperative.py`. Чиста версія -
   `process_rentals_pure` у `core.py`: усі параметри (мінімальна кількість днів,
   пороги знижки, ставки страхування) передаються явно, кожен запис у результаті -
   новий словник, жодного I/O.

2. **Завдання 2 - параметризація через `typing.Callable`.**
   Фабрика `make_processor(accept=…, apply_discount=…, insurance_fee=…)` повертає
   налаштований обробник. Політики:
   - `AcceptFn = Callable[[Rental], bool]` - фільтр (`make_min_days_filter`);
   - `DiscountFn = Callable[[Rental, float], float]` - знижка (`make_duration_discount`,
     `lift_price_fn`);
   - `InsuranceFn = Callable[[Rental, float], float]` - страховий збір
     (`make_class_insurance` - відсоток за класом авто, `make_per_day_insurance` -
     фіксована сума за день).

   Будь-яку політику можна замінити, не змінюючи обробник (див. «акційні політики» в `app.py`).

3. **Завдання 3 - ізоляція побічних ефектів.**
   Читання JSON, `print` та `time.time` живуть лише в `app.py`
   (`load_rentals`, `render_report`, `render_stamped`). Час інжектується в ядро як
   `NowFn = Callable[[], float]` (`stamp_total`, `stamp_report`), тому ядро лишається
   чистим і тестується з фейковим годинником.

4. **Додаткові вправи:** `compose`, `pipe` (знижка з кількох маленьких функцій:
   `make_percent_off`, `make_coupon`), `make_multiplier`, а також `mark_cancelled` і
   `totals_by_class` - перетворення списків без мутацій (comprehension замість
   накопичувальних змінних).

### Чисті функції предметної області

`base_price`, `is_confirmed`, `duration_discount_rate`, `insurance_rate_for`,
`with_pricing`, `summarize`, `process_rentals_pure`, `totals_by_class`, `mark_cancelled`.

### Формула розрахунку

```
base      = days * daily_rate
discount  = base * rate(days)            # 7+ днів: 10 %, 14+: 15 %, 30+: 25 %
insurance = (base - discount) * rate(car_class)   # economy 5 %, comfort 8 %, business 12 %, premium 18 %
total     = base - discount + insurance
```

До розрахунку беруться лише прокати зі статусом `confirmed` і тривалістю не менше
`min_days`.

## Структура

```
lab1/
  README.md               # цей файл
  core.py                 # ЧИСТЕ ядро: типи, функції, фабрики політик, compose
  app.py                  # оболонка I/O: читання JSON, друк звітів, time.time
  starter_imperative.py   # вихідний імперативний фрагмент (для порівняння)
  data/rentals.json       # тестові дані
  tests/conftest.py       # фікстура sample_rentals
  tests/test_core.py      # pytest-тести чистого ядра
  requirements.txt        # pytest, mypy, black, ruff
  pyproject.toml          # налаштування black / ruff / mypy / pytest
```

## Як запускати

```bash
pip install -r requirements.txt
```

Запуск програми (дані з `data/rentals.json` або з переданого файлу):

```bash
python app.py
```

```bash
python app.py data/rentals.json
```

Тести, перевірка типів, форматування та лінтер:

```bash
python -m pytest -q
```

```bash
python -m mypy
```

```bash
python -m black --check .
```

```bash
python -m ruff check .
```

## Тести

- `test_referential_transparency` - однаковий вхід дає однаковий результат;
- `test_no_mutation`, `test_processor_no_mutation`, `test_result_records_are_new_objects` -
  вхідні списки/словники не змінюються, результат складається з нових об'єктів;
- `test_callable_policies`, `test_processor_matches_pure_version`,
  `test_swapping_policy_changes_only_that_part` - коректність і замінюваність
  Callable-політик;
- `test_stamp_total_uses_injected_clock`, `test_stamp_report_does_not_mutate` - інжекція часу;
- `test_compose`, `test_pipe_builds_discount_from_small_functions`, `test_make_multiplier`,
  `test_mark_cancelled_returns_new_list`, `test_totals_by_class` - додаткові вправи;
- тести на окремі функції (`base_price`, `duration_discount_rate`, `insurance_rate_for`,
  `with_pricing`, `process_rentals_pure`).

Результат: 20 тестів проходять, `mypy --strict` без помилок, `black` і `ruff` чисто.

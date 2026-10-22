# Лабораторна робота №1. Основи функціонального програмування у Python

**Варіант 9 - Прокат автомобілів.** Для підтверджених прокатів обчислюється базова ціна, знижка за тривалість і страховий збір. Політики знижки та страхування передаються як функції через `typing.Callable`.

## Структура

- `core.py` - чисте ядро: функції без мутацій, глобалів та I/O, фабрика `make_processor`, `compose`, `make_multiplier`.
- `app.py` - оболонка побічних ефектів: тестові дані, друк звітів, `time.time`.
- `test/test_core.py` - pytest-тести: референтна прозорість, відсутність мутацій, Callable-політики.
- `requirements.txt` - pytest, mypy, black, ruff.

## Запуск

```bash
pip install -r requirements.txt
python app.py
python -m pytest test
python -m mypy --strict core.py app.py test/test_core.py
python -m black --check .
python -m ruff check .
```

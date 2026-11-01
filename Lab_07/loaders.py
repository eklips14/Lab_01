"""Поліморфне завантаження фільмів через @singledispatch (ЛР7, варіант 9).

Підтримуються: JSON-рядок, шлях str/Path до .json або .csv, відкритий
текстовий файл (JSON або CSV) і готовий список словників.
"""

import csv
import io
import json
from functools import singledispatch
from pathlib import Path
from typing import Any

Row = dict[str, Any]


def _from_json_text(text: str) -> list[Row]:
    """Розбирає JSON-масив об'єктів."""
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("JSON має містити список фільмів")
    return load_movies(data)


def _from_csv_text(text: str) -> list[Row]:
    """Розбирає CSV із заголовком."""
    return [dict(row) for row in csv.DictReader(io.StringIO(text))]


def _from_text(text: str) -> list[Row]:
    """Визначає формат вмісту: JSON починається з '[' або '{', інакше CSV."""
    stripped = text.strip()
    if stripped.startswith(("[", "{")):
        return _from_json_text(stripped)
    return _from_csv_text(text)


@singledispatch
def load_movies(src: object) -> list[Row]:
    """Повертає список сирих записів фільмів з різних джерел."""
    raise TypeError(f"Непідтримуваний тип джерела: {type(src)!r}")


@load_movies.register
def _(src: str) -> list[Row]:
    """JSON-рядок або шлях до файлу .json/.csv."""
    stripped = src.strip()
    if stripped.startswith(("[", "{")):
        return _from_json_text(stripped)
    return load_movies(Path(stripped))


@load_movies.register
def _(src: Path) -> list[Row]:
    """Файл .json або .csv."""
    text = src.read_text(encoding="utf-8")
    if src.suffix.lower() == ".json":
        return _from_json_text(text)
    if src.suffix.lower() == ".csv":
        return _from_csv_text(text)
    raise ValueError(f"Непідтримуване розширення: {src.suffix}")


@load_movies.register
def _(src: io.TextIOBase) -> list[Row]:
    """Відкритий текстовий файл з JSON або CSV."""
    return _from_text(src.read())


@load_movies.register
def _(src: list) -> list[Row]:  # type: ignore[type-arg]
    """Готовий список словників (повертається копія)."""
    if not all(isinstance(item, dict) for item in src):
        raise ValueError("Очікується список словників")
    return [dict(item) for item in src]

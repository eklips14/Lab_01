"""pytest-тести ЛР7, варіант 9."""

import io
import json
from functools import partial, reduce
from operator import itemgetter, mul
from pathlib import Path

import pytest

from core import (
    best_by_genre,
    clean_and_rank,
    filt,
    genre_is,
    mapf,
    normalize,
    pipeline,
    rating_at_least,
    sort_rank,
    titles,
    to_movies,
    top_n,
    total_votes,
    year_at_least,
)
from loaders import load_movies
from models import Movie, MovieRecord

ROWS = [
    {
        "title": " the matrix ",
        "genre": "Sci-Fi",
        "year": 1999,
        "rating": 8.7,
        "votes": 10,
    },
    {"title": "inception", "genre": "sci-fi", "year": 2010, "rating": 8.8, "votes": 30},
    {"title": "joker", "genre": "Drama", "year": 2019, "rating": 8.4, "votes": 20},
    {"title": "alpha", "genre": "Drama", "year": 2018, "rating": 8.4, "votes": 20},
    {"title": "cats", "genre": "Musical", "year": 2019, "rating": 2.8, "votes": 5},
]
CSV_TEXT = "title,genre,year,rating,votes\n" + "\n".join(
    f"{r['title']},{r['genre']},{r['year']},{r['rating']},{r['votes']}" for r in ROWS
)


def test_pipeline_order_and_empty() -> None:
    """Тест: pipeline застосовує функції зліва направо."""
    assert pipeline(3, lambda x: x + 1, lambda x: x * 2, lambda x: x + 1) == 9
    assert pipeline(5) == 5


def test_reduce_initial_value() -> None:
    """Тест: reduce з початковим значенням на порожній послідовності."""
    assert reduce(mul, [], 1) == 1


def test_partial_filters() -> None:
    """Тест: partial фіксує параметри фільтрів."""
    records = [normalize(r) for r in ROWS]
    recent = list(filt(partial(year_at_least, 2010))(records))
    assert [r["title"] for r in recent] == ["Inception", "Joker", "Alpha", "Cats"]
    good = list(filt(partial(rating_at_least, 8.5))(records))
    assert [r["title"] for r in good] == ["The Matrix", "Inception"]
    drama = list(filt(partial(genre_is, "DRAMA"))(records))
    assert len(drama) == 2


def test_normalize_with_operator() -> None:
    """Тест: нормалізація рядків і типів через itemgetter/methodcaller."""
    row = {
        "title": "  the matrix ",
        "genre": " Sci-Fi",
        "year": "1999",
        "rating": "8.7",
        "votes": "10",
    }
    assert normalize(row) == {
        "title": "The Matrix",
        "genre": "sci-fi",
        "year": 1999,
        "rating": 8.7,
        "votes": 10,
    }


def test_sort_rank_multi_key() -> None:
    """Тест: rating спадно, votes спадно, title зростанням."""
    ranked = sort_rank(map(normalize, ROWS))
    assert [r["title"] for r in ranked] == [
        "Inception",
        "The Matrix",
        "Alpha",
        "Joker",
        "Cats",
    ]


def test_itemgetter_multiple_keys() -> None:
    """Тест: itemgetter для кількох ключів."""
    rows = [{"a": 1, "b": 2}, {"a": 1, "b": 1}, {"a": 0, "b": 9}]
    assert sorted(rows, key=itemgetter("a", "b")) == [
        {"a": 0, "b": 9},
        {"a": 1, "b": 1},
        {"a": 1, "b": 2},
    ]


def test_clean_and_rank_top() -> None:
    """Тест: повний конвеєр з Top-N."""
    result = clean_and_rank(ROWS, top=2, min_year=2000, min_rating=8.0)
    assert [r["title"] for r in result] == ["Inception", "Alpha"]
    assert clean_and_rank(ROWS, top=0) == []


def test_singledispatch_all_sources(tmp_path: Path) -> None:
    """Тест: усі типи джерел (рядок, шлях, Path, файл, список) дають один результат."""
    json_file = tmp_path / "movies.json"
    csv_file = tmp_path / "movies.csv"
    json_file.write_text(json.dumps(ROWS), encoding="utf-8")
    csv_file.write_text(CSV_TEXT, encoding="utf-8")
    expected = clean_and_rank(ROWS, top=3)
    with json_file.open(encoding="utf-8") as jf, csv_file.open(encoding="utf-8") as cf:
        sources: list[object] = [
            json.dumps(ROWS),
            str(json_file),
            json_file,
            str(csv_file),
            csv_file,
            jf,
            cf,
            io.StringIO(CSV_TEXT),
        ]
        for src in sources:
            assert clean_and_rank(src, top=3) == expected


def test_load_list_returns_copy() -> None:
    """Тест: список словників повертається копією."""
    loaded = load_movies(ROWS)
    loaded[0]["title"] = "changed"
    assert ROWS[0]["title"] == " the matrix "


def test_loader_errors(tmp_path: Path) -> None:
    """Тест: непідтримувані джерела."""
    with pytest.raises(TypeError):
        load_movies(42)
    with pytest.raises(ValueError):
        load_movies([1, 2])
    with pytest.raises(ValueError):
        load_movies('{"title": "x"}')
    bad = tmp_path / "movies.txt"
    bad.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        load_movies(bad)


def test_reduce_and_attrgetter() -> None:
    """Тест: total_votes через reduce, titles через attrgetter."""
    records = [normalize(r) for r in ROWS]
    assert total_votes(records) == 85
    assert titles(to_movies(records[:2])) == ["The Matrix", "Inception"]


def test_best_by_genre() -> None:
    """Тест: найкращий фільм кожного жанру."""
    best = best_by_genre(to_movies(map(normalize, ROWS)))
    assert {g: m.title for g, m in best.items()} == {
        "sci-fi": "Inception",
        "drama": "Joker",
        "musical": "Cats",
    }


def movie(title: str, rating: float, votes: int) -> Movie:
    """Скорочений конструктор Movie для тестів."""
    return Movie(title=title, genre="drama", year=2020, rating=rating, votes=votes)


def test_total_ordering_all_operators() -> None:
    """Тест: усі оператори порівняння."""
    low, high = movie("A", 7.0, 10), movie("B", 8.0, 5)
    same = movie("A", 7.0, 10)
    assert low < high and low <= high and high > low and high >= low
    assert low == same and low != high and low <= same and low >= same
    assert movie("A", 8.0, 1) < movie("A", 8.0, 2) < movie("B", 8.0, 2)


def test_ordering_with_other_types() -> None:
    """Тест: для чужих типів повертається NotImplemented."""
    m = movie("A", 7.0, 10)
    assert (m == 5) is False
    assert m.__lt__(5) is NotImplemented
    with pytest.raises(TypeError):
        _ = m < 5


def test_sorted_max_and_hash() -> None:
    """Тест: sorted, max та узгоджений хеш."""
    movies = [movie("B", 8.0, 5), movie("A", 7.0, 10), movie("C", 9.0, 1)]
    assert [m.title for m in sorted(movies)] == ["A", "B", "C"]
    assert max(movies).title == "C"
    assert len({movie("A", 7.0, 10), movie("A", 7.0, 10)}) == 1


def test_top_n_helper() -> None:
    """Тест: top_n з від'ємним і великим n."""
    records: list[MovieRecord] = [normalize(r) for r in ROWS]
    assert top_n(-1)(records) == []
    assert len(top_n(100)(records)) == len(records)
    assert list(mapf(lambda r: r["year"])(records[:2])) == [1999, 2010]

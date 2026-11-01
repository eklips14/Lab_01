"""Конвеєр ЛР7, варіант 9: partial + reduce + operator над фільмами."""

from collections.abc import Callable, Iterable, Mapping
from functools import partial, reduce
from itertools import islice
from operator import add, attrgetter, itemgetter, methodcaller
from typing import Any

from loaders import load_movies
from models import Movie, MovieRecord

get_title = itemgetter("title")
get_genre = itemgetter("genre")
get_year = itemgetter("year")
get_rating = itemgetter("rating")
get_votes = itemgetter("votes")
strip = methodcaller("strip")
to_title = methodcaller("title")
to_lower = methodcaller("lower")


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Пропускає значення через функції зліва направо (functools.reduce)."""
    return reduce(lambda acc, f: f(acc), funcs, value)


def mapf(fn: Callable[[Any], Any]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """map із зафіксованою функцією (partial)."""
    return partial(map, fn)


def filt(pred: Callable[[Any], bool]) -> Callable[[Iterable[Any]], Iterable[Any]]:
    """filter із зафіксованим предикатом (partial)."""
    return partial(filter, pred)


def normalize(row: Mapping[str, object]) -> MovieRecord:
    """Очищує рядки та приводить типи (itemgetter + methodcaller)."""
    return {
        "title": to_title(strip(str(get_title(row)))),
        "genre": to_lower(strip(str(get_genre(row)))),
        "year": int(str(get_year(row))),
        "rating": float(str(get_rating(row))),
        "votes": int(str(get_votes(row))),
    }


def year_at_least(min_year: int, movie: MovieRecord) -> bool:
    """Фільм не старший за min_year."""
    return movie["year"] >= min_year


def rating_at_least(min_rating: float, movie: MovieRecord) -> bool:
    """Рейтинг не нижчий за min_rating."""
    return movie["rating"] >= min_rating


def genre_is(genre: str, movie: MovieRecord) -> bool:
    """Фільм належить жанру."""
    return movie["genre"] == genre.lower()


def sort_rank(records: Iterable[MovieRecord]) -> list[MovieRecord]:
    """Сортує: rating спадно, votes спадно, title зростанням (стабільний sorted)."""
    by_title = sorted(records, key=get_title)
    return sorted(by_title, key=itemgetter("rating", "votes"), reverse=True)


def top_n(n: int) -> Callable[[Iterable[MovieRecord]], list[MovieRecord]]:
    """Бере перші n записів."""
    return lambda records: list(islice(records, max(n, 0)))


def clean_and_rank(
    src: object,
    top: int = 3,
    *,
    min_year: int = 2000,
    min_rating: float = 7.0,
    genre: str | None = None,
) -> list[MovieRecord]:
    """Завантажує, нормалізує, фільтрує, сортує і повертає Top-N фільмів."""
    filters = [
        filt(partial(year_at_least, min_year)),
        filt(partial(rating_at_least, min_rating)),
    ]
    if genre is not None:
        filters.append(filt(partial(genre_is, genre)))
    result: list[MovieRecord] = pipeline(
        src, load_movies, mapf(normalize), *filters, sort_rank, top_n(top)
    )
    return result


def to_movies(records: Iterable[MovieRecord]) -> list[Movie]:
    """Перетворює записи на об'єкти Movie."""
    return list(map(Movie.from_record, records))


def total_votes(records: Iterable[MovieRecord]) -> int:
    """Сумарна кількість голосів через reduce."""
    return reduce(add, map(get_votes, records), 0)


def best_by_genre(movies: Iterable[Movie]) -> dict[str, Movie]:
    """Найкращий фільм кожного жанру (reduce + порівняння total_ordering)."""
    get = attrgetter("genre")
    return reduce(
        lambda acc, m: {**acc, get(m): max(acc.get(get(m), m), m)},
        movies,
        dict[str, Movie](),
    )


def titles(movies: Iterable[Movie]) -> list[str]:
    """Назви фільмів через attrgetter."""
    return list(map(attrgetter("title"), movies))

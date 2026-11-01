"""Моделі ЛР7, варіант 9: нормалізований запис фільму та клас Movie."""

from dataclasses import dataclass
from functools import total_ordering
from typing import TypedDict


class MovieRecord(TypedDict):
    """Нормалізований запис фільму."""

    title: str
    genre: str
    year: int
    rating: float
    votes: int


@total_ordering
@dataclass(frozen=True, eq=False)
class Movie:
    """Фільм із порядком за rating, потім votes, потім title.

    Достатньо __eq__ та __lt__, решту порівнянь добудовує @total_ordering.
    """

    title: str
    genre: str
    year: int
    rating: float
    votes: int

    def _key(self) -> tuple[float, int, str]:
        """Ключ порівняння."""
        return self.rating, self.votes, self.title

    def __eq__(self, other: object) -> bool:
        """Рівність за ключем; для чужих типів - NotImplemented."""
        if not isinstance(other, Movie):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        """Менше за ключем; для чужих типів - NotImplemented."""
        if not isinstance(other, Movie):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        """Хеш узгоджений з __eq__."""
        return hash(self._key())

    @classmethod
    def from_record(cls, record: MovieRecord) -> "Movie":
        """Створює Movie з нормалізованого запису."""
        return cls(**record)

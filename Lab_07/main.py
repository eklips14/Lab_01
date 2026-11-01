"""Точка входу лабораторної роботи №7, варіант 9."""

from pathlib import Path

from core import (
    best_by_genre,
    clean_and_rank,
    mapf,
    normalize,
    pipeline,
    to_movies,
    total_votes,
)
from loaders import load_movies

DATA_DIR = Path(__file__).parent


def run() -> None:
    """Демонструє конвеєр, singledispatch і total_ordering."""
    json_path = DATA_DIR / "sample_data.json"
    csv_path = DATA_DIR / "sample_data.csv"

    print("Top-3 фільми з 2000 року, рейтинг від 7.0 (JSON):")
    for m in clean_and_rank(json_path, top=3):
        print(f"  {m['title']:<20} {m['year']}  {m['rating']}  {m['votes']:>9}")

    print("\nTop-2 sci-fi (CSV, шлях рядком):")
    for m in clean_and_rank(str(csv_path), top=2, genre="Sci-Fi"):
        print(f"  {m['title']:<20} {m['rating']}")

    same = clean_and_rank(json_path, top=5) == clean_and_rank(csv_path, top=5)
    print(f"\nJSON і CSV дають однаковий результат: {same}")

    records = pipeline(json_path, load_movies, mapf(normalize), list)
    movies = to_movies(records)
    print(f"Сумарно голосів: {total_votes(records):,}")
    print(f"Найкращий фільм (max за total_ordering): {max(movies).title}")
    for genre, movie in sorted(best_by_genre(movies).items()):
        print(f"  найкращий у жанрі {genre:<8}: {movie.title}")
    inception, interstellar = movies[0], movies[1]
    print(f"Inception > Interstellar: {inception > interstellar}")


def main() -> None:
    """Запуск демонстрації functools та operator."""
    run()


if __name__ == "__main__":
    main()

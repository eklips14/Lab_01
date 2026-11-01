"""Точка входу лабораторної роботи №4, варіант 9."""

import sys
import time
from collections.abc import Callable

from algorithms import fib, fib_iter, fib_naive, quicksort
from maze import (
    bfs_shortest_path,
    count_paths_from,
    count_paths_memo,
    count_paths_naive,
    dfs_path_iterative,
    dfs_path_recursive,
    open_grid,
    parse_maze,
    render_path,
)

MAZE_TEXT = """
S.#.......
.##.####..
....#..#.#
#.#.#.##..
..#...#..F
"""


def measure(fn: Callable[[], object], repeat: int = 1) -> float:
    """Повертає час виконання в мілісекундах."""
    start = time.perf_counter()
    for _ in range(repeat):
        fn()
    return (time.perf_counter() - start) * 1000 / repeat


def run() -> None:
    """Демонструє пошук шляху та порівняння рекурсії, ітерації і мемоізації."""
    maze = parse_maze(MAZE_TEXT.splitlines())
    print("Лабіринт:")
    print("\n".join(maze))
    for name, finder in [
        ("рекурсивний DFS", dfs_path_recursive),
        ("ітеративний DFS", dfs_path_iterative),
        ("BFS (найкоротший)", bfs_shortest_path),
    ]:
        path = finder(maze)
        assert path is not None
        print(f"\n{name}: {len(path) - 1} кроків")
        print("\n".join(render_path(maze, path)))

    print(f"\nЛіміт рекурсії CPython: {sys.getrecursionlimit()}")
    grid = open_grid(11, 11)
    count_paths_from.cache_clear()
    t_naive = measure(lambda: count_paths_naive(grid))
    t_memo = measure(lambda: count_paths_memo(grid))
    print(f"Шляхів 11x11 вниз/вправо: {count_paths_memo(grid)}")
    print(f"  без кешу: {t_naive:.2f} мс, з lru_cache: {t_memo:.2f} мс")
    print(f"  {count_paths_from.cache_info()}")
    t_rec = measure(lambda: dfs_path_recursive(open_grid(30, 30)), 20)
    t_it = measure(lambda: dfs_path_iterative(open_grid(30, 30)), 20)
    print(f"DFS 30x30: рекурсивний {t_rec:.2f} мс, ітеративний {t_it:.2f} мс")
    print(f"fib(25): naive {measure(lambda: fib_naive(25)):.2f} мс, ", end="")
    fib.cache_clear()
    print(f"lru_cache {measure(lambda: fib(25)):.3f} мс, ", end="")
    print(f"iter {measure(lambda: fib_iter(25)):.3f} мс")
    print(f"quicksort([5, 3, 8, 1, 9, 2]) = {quicksort([5, 3, 8, 1, 9, 2])}")


def main() -> None:
    """Запуск демонстрації рекурсії та мемоізації."""
    run()


if __name__ == "__main__":
    main()

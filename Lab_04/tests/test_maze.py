"""Тести варіанта 9: лабіринт."""

from collections.abc import Callable

import pytest

from maze import (
    Maze,
    Path,
    bfs_shortest_path,
    count_paths_from,
    count_paths_memo,
    count_paths_naive,
    dfs_path_iterative,
    dfs_path_recursive,
    is_valid_path,
    open_grid,
    parse_maze,
    render_path,
)

MAZE: Maze = parse_maze(
    [
        "S.#....",
        ".##.##.",
        "...#...",
        "#.....F",
    ]
)

Finder = Callable[[Maze], Path | None]
FINDERS: list[Finder] = [dfs_path_recursive, dfs_path_iterative, bfs_shortest_path]


@pytest.mark.parametrize("finder", FINDERS)
def test_path_found_and_valid(finder: Finder) -> None:
    """Тест: кожен алгоритм знаходить коректний шлях."""
    path = finder(MAZE)
    assert path is not None
    assert is_valid_path(MAZE, path)


def test_bfs_is_shortest() -> None:
    """Тест: BFS дає шлях не довший за DFS."""
    bfs = bfs_shortest_path(MAZE)
    dfs = dfs_path_recursive(MAZE)
    assert bfs is not None and dfs is not None
    assert len(bfs) == 10
    assert len(bfs) <= len(dfs)


@pytest.mark.parametrize("finder", FINDERS)
def test_no_path(finder: Finder) -> None:
    """Тест: якщо фініш відрізано стіною, шляху немає."""
    blocked = parse_maze(["S.#F", "..#."])
    assert finder(blocked) is None


def test_start_is_finish_neighbor() -> None:
    """Тест: найпростіший випадок - фініш поруч зі стартом."""
    tiny = parse_maze(["SF"])
    assert dfs_path_recursive(tiny) == ((0, 0), (0, 1))


def test_input_not_mutated() -> None:
    """Тест: пошук і рендер не змінюють вхідну карту."""
    before = tuple(MAZE)
    path = dfs_path_recursive(MAZE)
    assert path is not None
    marked = render_path(MAZE, path)
    assert MAZE == before
    assert marked != MAZE and "*" in "".join(marked)


def test_parse_maze_errors() -> None:
    """Тест: непрямокутний і порожній лабіринт - помилка."""
    with pytest.raises(ValueError):
        parse_maze(["S..", ".F"])
    with pytest.raises(ValueError):
        parse_maze([])


def test_count_paths_memo_matches_naive() -> None:
    """Тест: мемоізована версія дає той самий результат, що й наївна."""
    grid = open_grid(6, 6)
    assert count_paths_naive(grid) == count_paths_memo(grid) == 252
    assert count_paths_memo(MAZE) == count_paths_naive(MAZE)


def test_cache_info_and_clear() -> None:
    """Тест: cache_info показує влучання, cache_clear очищає кеш."""
    count_paths_from.cache_clear()
    count_paths_memo(open_grid(5, 5))
    info = count_paths_from.cache_info()
    assert info.hits > 0 and info.currsize > 0
    count_paths_from.cache_clear()
    assert count_paths_from.cache_info().currsize == 0


def test_deep_maze_recursion_limit() -> None:
    """Тест: глибокий коридор ламає рекурсію, ітеративна версія працює."""
    corridor = open_grid(1, 3000)
    with pytest.raises(RecursionError):
        dfs_path_recursive(corridor)
    path = dfs_path_iterative(corridor)
    assert path is not None and len(path) == 3000

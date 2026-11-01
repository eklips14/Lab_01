"""Варіант 9 ЛР4: пошук шляху в лабіринті рекурсією та ітерацією.

Лабіринт - tuple рядків: '#' стіна, '.' прохід, 'S' старт, 'F' фініш.
Вхідна карта ніколи не змінюється.
"""

from collections import deque
from collections.abc import Iterable
from functools import lru_cache
from itertools import pairwise

type Cell = tuple[int, int]
type Maze = tuple[str, ...]
type Path = tuple[Cell, ...]

WALL = "#"
START = "S"
FINISH = "F"
MOVES: tuple[Cell, ...] = ((0, 1), (1, 0), (0, -1), (-1, 0))


def parse_maze(lines: Iterable[str]) -> Maze:
    """Перетворює рядки на незмінний прямокутний лабіринт."""
    maze = tuple(line.strip() for line in lines if line.strip())
    if not maze or len({len(row) for row in maze}) != 1:
        raise ValueError("Лабіринт має бути непорожнім і прямокутним")
    return maze


def find(maze: Maze, ch: str) -> Cell:
    """Знаходить координати символу."""
    for r, row in enumerate(maze):
        c = row.find(ch)
        if c >= 0:
            return r, c
    raise ValueError(f"Символ {ch!r} не знайдено")


def is_open(maze: Maze, cell: Cell) -> bool:
    """Чи клітинка в межах карти і не є стіною."""
    r, c = cell
    return 0 <= r < len(maze) and 0 <= c < len(maze[0]) and maze[r][c] != WALL


def neighbors(maze: Maze, cell: Cell) -> tuple[Cell, ...]:
    """Сусідні прохідні клітинки."""
    r, c = cell
    return tuple(
        (r + dr, c + dc) for dr, dc in MOVES if is_open(maze, (r + dr, c + dc))
    )


def dfs_path_recursive(maze: Maze) -> Path | None:
    """Рекурсивний DFS. Множина відвіданих передається далі, а не мутується."""
    start, finish = find(maze, START), find(maze, FINISH)

    def walk(cell: Cell, seen: frozenset[Cell]) -> tuple[Path | None, frozenset[Cell]]:
        """База: фініш. Крок: спробувати кожного невідвіданого сусіда."""
        if cell == finish:
            return (cell,), seen
        for nxt in neighbors(maze, cell):
            if nxt in seen:
                continue
            rest, seen = walk(nxt, seen | {nxt})
            if rest is not None:
                return (cell, *rest), seen
        return None, seen

    return walk(start, frozenset({start}))[0]


def dfs_path_iterative(maze: Maze) -> Path | None:
    """Ітеративний DFS з власним стеком (не впирається в ліміт рекурсії)."""
    start, finish = find(maze, START), find(maze, FINISH)
    stack: list[Path] = [(start,)]
    seen = {start}
    while stack:
        path = stack.pop()
        if path[-1] == finish:
            return path
        for nxt in reversed(neighbors(maze, path[-1])):
            if nxt not in seen:
                seen.add(nxt)
                stack.append((*path, nxt))
    return None


def bfs_shortest_path(maze: Maze) -> Path | None:
    """BFS: найкоротший шлях за кількістю кроків."""
    start, finish = find(maze, START), find(maze, FINISH)
    queue: deque[Path] = deque([(start,)])
    seen = {start}
    while queue:
        path = queue.popleft()
        if path[-1] == finish:
            return path
        for nxt in neighbors(maze, path[-1]):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((*path, nxt))
    return None


def is_valid_path(maze: Maze, path: Path) -> bool:
    """Перевіряє, що шлях іде від S до F сусідніми прохідними клітинками."""
    if not path or path[0] != find(maze, START) or path[-1] != find(maze, FINISH):
        return False
    steps_ok = all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in pairwise(path))
    return steps_ok and all(is_open(maze, cell) for cell in path)


def render_path(maze: Maze, path: Path) -> Maze:
    """Повертає НОВУ карту, де шлях позначено '*'."""
    marks = set(path)
    return tuple(
        "".join(
            "*" if (r, c) in marks and ch not in (START, FINISH) else ch
            for c, ch in enumerate(row)
        )
        for r, row in enumerate(maze)
    )


def count_paths_naive(maze: Maze) -> int:
    """Кількість шляхів S->F кроками вниз/вправо без кешу (експоненційно)."""
    finish = find(maze, FINISH)

    def go(r: int, c: int) -> int:
        """База: стіна/вихід за межі - 0, фініш - 1."""
        if not is_open(maze, (r, c)):
            return 0
        if (r, c) == finish:
            return 1
        return go(r + 1, c) + go(r, c + 1)

    return go(*find(maze, START))


@lru_cache(maxsize=None)
def count_paths_from(maze: Maze, r: int, c: int) -> int:
    """Мемоізована кількість шляхів з (r, c) до фінішу кроками вниз/вправо."""
    if not is_open(maze, (r, c)):
        return 0
    if (r, c) == find(maze, FINISH):
        return 1
    return count_paths_from(maze, r + 1, c) + count_paths_from(maze, r, c + 1)


def count_paths_memo(maze: Maze) -> int:
    """Кількість шляхів S->F з мемоізацією через lru_cache."""
    return count_paths_from(maze, *find(maze, START))


def open_grid(rows: int, cols: int) -> Maze:
    """Порожній лабіринт rows x cols зі стартом у лівому верхньому кутку."""
    middle = "." * cols
    first = START + middle[1:]
    last = middle[:-1] + FINISH
    if rows == 1:
        return (START + "." * (cols - 2) + FINISH,)
    return (first, *([middle] * (rows - 2)), last)

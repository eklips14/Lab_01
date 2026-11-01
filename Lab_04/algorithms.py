"""Базова частина ЛР4: quicksort, обходи дерева, мемоізований Фібоначчі."""

from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import lru_cache
from random import choice


def quicksort(xs: Sequence[int]) -> list[int]:
    """Чистий рекурсивний quicksort з випадковим pivot (вхід не змінюється)."""
    if len(xs) <= 1:
        return list(xs)
    pivot = choice(xs)
    left = [x for x in xs if x < pivot]
    mid = [x for x in xs if x == pivot]
    right = [x for x in xs if x > pivot]
    return quicksort(left) + mid + quicksort(right)


@dataclass(frozen=True, slots=True)
class Node:
    """Вузол бінарного дерева."""

    key: int
    left: "Node | None" = None
    right: "Node | None" = None


def preorder(t: Node | None) -> Iterator[int]:
    """Рекурсивний прямий обхід: корінь, ліве, праве."""
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Node | None) -> Iterator[int]:
    """Рекурсивний симетричний обхід: ліве, корінь, праве."""
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Node | None) -> Iterator[int]:
    """Рекурсивний зворотний обхід: ліве, праве, корінь."""
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Node | None) -> list[int]:
    """Ітеративний обхід у ширину через чергу."""
    if t is None:
        return []
    queue, out = deque([t]), []
    while queue:
        node = queue.popleft()
        out.append(node.key)
        queue.extend(child for child in (node.left, node.right) if child)
    return out


def dfs_preorder_iter(t: Node | None) -> list[int]:
    """Ітеративний прямий обхід через власний стек."""
    if t is None:
        return []
    stack, out = [t], []
    while stack:
        node = stack.pop()
        out.append(node.key)
        stack.extend(child for child in (node.right, node.left) if child)
    return out


def height(t: Node | None) -> int:
    """Висота дерева рекурсивно."""
    if t is None:
        return 0
    return 1 + max(height(t.left), height(t.right))


def height_iter(t: Node | None) -> int:
    """Висота дерева ітеративно (обхід рівнями)."""
    level = [t] if t else []
    depth = 0
    while level:
        depth += 1
        level = [c for n in level for c in (n.left, n.right) if c]
    return depth


@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Мемоізований рекурсивний Фібоначчі: O(n) замість O(2^n)."""
    if n < 0:
        raise ValueError("n має бути невід'ємним")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_naive(n: int) -> int:
    """Рекурсивний Фібоначчі без кешу (експоненційний)."""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_iter(n: int) -> int:
    """Ітеративний Фібоначчі без рекурсії та стеку."""
    if n < 0:
        raise ValueError("n має бути невід'ємним")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fact(n: int, acc: int = 1) -> int:
    """Хвостова рекурсія. CPython не має TCO, тож стек усе одно росте."""
    if n <= 1:
        return acc
    return fact(n - 1, acc * n)

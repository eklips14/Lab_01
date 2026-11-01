"""Тести accumulate."""

import operator
from itertools import accumulate

from streams import prefix_products, prefix_sums


def test_accumulate_sum_prod() -> None:
    """Тест: префіксні суми і добутки."""
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(accumulate([1, 2, 3, 4], operator.mul)) == [1, 2, 6, 24]
    assert list(prefix_sums([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(prefix_products([1, 2, 3, 4])) == [1, 2, 6, 24]


def test_accumulate_max_and_empty() -> None:
    """Тест: префіксний максимум і порожній вхід."""
    assert list(accumulate([3, 1, 4, 1, 5], max)) == [3, 3, 4, 4, 5]
    assert list(prefix_sums([])) == []

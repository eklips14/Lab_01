"""Точка входу лабораторної роботи №8, варіант 9."""

from dataclasses import dataclass

from evaluator import count_nodes, depth, from_python, get, stats, with_field
from model import JSON, JNumber, JObject, JString
from pretty import pretty, render, tree


@dataclass(frozen=True)
class Car:
    """Довільний клас, що підходить під протокол SupportsToJSON."""

    model: str
    price: int

    def to_json(self) -> JSON:
        """JSON-представлення автомобіля."""
        return JObject((("model", JString(self.model)), ("price", JNumber(self.price))))


def run() -> None:
    """Демонструє ADT, match/case та операції над JSON-деревом."""
    doc = from_python(
        {
            "company": "Прокат авто",
            "active": True,
            "rating": 4.7,
            "manager": None,
            "cars": [Car("Skoda Octavia", 1200), Car("Toyota RAV4", 1900)],
            "tags": ["economy", "suv"],
        }
    )
    print("Компактно:", render(doc))
    print("\nЗ відступами:\n" + pretty(doc))
    print("\nДерево:\n" + tree(doc))
    print(f"\nВузлів: {count_nodes(doc)}, глибина: {depth(doc)}")
    print(f"Статистика за типами: {stats(doc)}")
    print(f"cars[1].model = {render(get(doc, 'cars', 1, 'model') or JString('?'))}")
    if isinstance(doc, JObject):
        updated = with_field(doc, "rating", JNumber(4.9))
        print(
            f"Новий rating: {render(get(updated, 'rating') or JString('?'))}, ", end=""
        )
        print(f"старий не змінився: {render(get(doc, 'rating') or JString('?'))}")


def main() -> None:
    """Запуск демонстрації JSON-дерева."""
    run()


if __name__ == "__main__":
    main()

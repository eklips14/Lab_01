"""Точка входу лабораторної роботи №3, варіант 9."""

from core import add_label, add_route_point, change_status, parcel_cost, update_meta
from model import Parcel, make_meta


def run() -> None:
    """Демонструє pure-оновлення незмінної посилки."""
    parcel = Parcel(
        id=101,
        sender="Нова пошта",
        weight_kg=2.5,
        meta=make_meta(source="web", region="Lviv"),
    )
    step1 = add_route_point(parcel, "Львів", "Сортувальний центр", 4.0)
    step2 = add_route_point(step1, "Київ", "Хаб-2", 6.5)
    step3 = add_label(step2, "express")
    step4 = change_status(step3, "in_transit")
    step5 = update_meta(step4, courier="Petro")

    for name, p in [("початкова", parcel), ("після оновлень", step5)]:
        print(f"--- {name} ---")
        print(f"статус: {p.status}, мітки: {sorted(p.labels)}")
        print(f"маршрут: {[pt.city for pt in p.route]}, годин: {p.total_hours()}")
        print(f"meta: {dict(p.meta)}, вартість: {parcel_cost(p)} грн")
    print(
        f"\nоригінал не змінився: {parcel.route == () and parcel.status == 'created'}"
    )
    print(f"нова копія: {step5 is not parcel}, hash: {hash(step5) != hash(parcel)}")


def main() -> None:
    """Запуск демонстрації незмінної моделі доставки."""
    run()


if __name__ == "__main__":
    main()

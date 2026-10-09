"""Стартовий ІМПЕРАТИВНИЙ фрагмент (варіант 9 - прокат автомобілів).

Цей файл залишено лише для порівняння: тут є всі "погані" практики,
які переписано у функціональному стилі в core.py / app.py:

* глобальні константи INSURANCE_RATE та LONG_RENTAL_DISCOUNT усередині обчислень;
* print() прямо в циклі (I/O змішано з обчисленнями);
* мутація вхідних словників (r["total"] = ...);
* накопичувальні змінні, які змінюються на кожній ітерації.
"""

INSURANCE_RATE = 0.1  # глобальний стан
LONG_RENTAL_DISCOUNT = 0.15  # глобальний стан


def process_rentals(rentals, min_days):  # type: ignore[no-untyped-def]
    # rentals: список словників
    # {'id': int, 'car_class': str, 'days': int, 'daily_rate': float, 'status': str}
    valid = []
    total_revenue = 0.0

    for r in rentals:
        if r["status"] != "confirmed":
            continue
        # побічний ефект
        print("Processing rental:", r["id"])

        # мутація локальної змінної
        price = r["days"] * r["daily_rate"]
        if r["days"] < min_days:
            continue

        # глобали всередині обчислень
        if r["days"] >= 7:
            price = price * (1 - LONG_RENTAL_DISCOUNT)
        price = price + price * INSURANCE_RATE

        r["total"] = price  # мутуємо вхідні дані
        valid.append(r)
        total_revenue += price

    return {"count": len(valid), "revenue": total_revenue, "rentals": valid}

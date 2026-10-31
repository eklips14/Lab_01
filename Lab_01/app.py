from core import (
    Rental,
    Report,
    lift_price_fn,
    make_class_insurance,
    make_coupon,
    make_duration_discount,
    make_min_days_filter,
    make_per_day_insurance,
    make_percent_off,
    make_processor,
    pipe,
    process_rentals_pure,
    totals_by_class,
)


def render_report(title: str, report: Report) -> None:
    """Друкує звіт (I/O)."""
    print(f"=== {title} ===")
    print(
        f"{'ID':>4} {'Клас':<10} {'Днів':>4} {'База':>10} {'Знижка':>9} "
        f"{'Страх.':>9} {'Разом':>10}"
    )
    for r in report["rentals"]:
        print(
            f"{r['id']:>4} {r['car_class']:<10} {r['days']:>4} "
            f"{r['base_price']:>10.2f} {r['discount']:>9.2f} "
            f"{r['insurance']:>9.2f} {r['total']:>10.2f}"
        )
    print(f"Прийнято прокатів: {report['count']}")
    print(f"Дохід:            {report['revenue']:.2f}")
    for car_class, total in totals_by_class(report["rentals"]).items():
        print(f"  {car_class:<10} {total:>10.2f}")
    print()


def run() -> None:
    """Запускає обробку прокатів та виводить результати."""
    rentals: list[Rental] = [
        {
            "id": 1,
            "car_class": "economy",
            "days": 3,
            "daily_rate": 800.0,
            "status": "confirmed",
        },
        {
            "id": 2,
            "car_class": "comfort",
            "days": 7,
            "daily_rate": 1200.0,
            "status": "confirmed",
        },
        {
            "id": 3,
            "car_class": "business",
            "days": 1,
            "daily_rate": 2500.0,
            "status": "confirmed",
        },
        {
            "id": 4,
            "car_class": "premium",
            "days": 14,
            "daily_rate": 4000.0,
            "status": "confirmed",
        },
        {
            "id": 5,
            "car_class": "economy",
            "days": 10,
            "daily_rate": 750.0,
            "status": "cancelled",
        },
        {
            "id": 6,
            "car_class": "comfort",
            "days": 30,
            "daily_rate": 1100.0,
            "status": "confirmed",
        },
        {
            "id": 7,
            "car_class": "business",
            "days": 5,
            "daily_rate": 2300.0,
            "status": "pending",
        },
        {
            "id": 8,
            "car_class": "suv",
            "days": 4,
            "daily_rate": 1900.0,
            "status": "confirmed",
        },
    ]
    discount_tiers = ((7, 0.10), (14, 0.15), (30, 0.25))
    insurance_rates = {
        "economy": 0.05,
        "comfort": 0.08,
        "business": 0.12,
        "premium": 0.18,
    }

    basic = process_rentals_pure(
        rentals,
        min_days=2,
        discount_tiers=discount_tiers,
        insurance_rates=insurance_rates,
        default_insurance_rate=0.10,
    )
    render_report("Завдання 1: process_rentals_pure", basic)

    standard = make_processor(
        accept=make_min_days_filter(2),
        apply_discount=make_duration_discount(discount_tiers),
        insurance_fee=make_class_insurance(insurance_rates, default=0.10),
    )
    render_report("Завдання 2: make_processor (стандартні політики)", standard(rentals))

    promo = make_processor(
        accept=make_min_days_filter(1),
        apply_discount=lift_price_fn(pipe(make_percent_off(5), make_coupon(50.0))),
        insurance_fee=make_per_day_insurance(15.0),
    )
    render_report("Завдання 2: make_processor (акційні політики)", promo(rentals))


if __name__ == "__main__":
    run()

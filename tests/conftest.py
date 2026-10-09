from __future__ import annotations

import pytest

from core import Rental


@pytest.fixture
def sample_rentals() -> list[Rental]:
    return [
        {
            "id": 1,
            "car_class": "economy",
            "days": 3,
            "daily_rate": 100.0,
            "status": "confirmed",
        },
        {
            "id": 2,
            "car_class": "comfort",
            "days": 7,
            "daily_rate": 200.0,
            "status": "confirmed",
        },
        {
            "id": 3,
            "car_class": "business",
            "days": 1,
            "daily_rate": 500.0,
            "status": "confirmed",
        },
        {
            "id": 4,
            "car_class": "premium",
            "days": 30,
            "daily_rate": 400.0,
            "status": "confirmed",
        },
        {
            "id": 5,
            "car_class": "economy",
            "days": 10,
            "daily_rate": 100.0,
            "status": "cancelled",
        },
        {
            "id": 6,
            "car_class": "suv",
            "days": 2,
            "daily_rate": 300.0,
            "status": "pending",
        },
    ]

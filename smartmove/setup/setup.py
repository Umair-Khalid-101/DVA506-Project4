from factories.vehicle_factory import VehicleFactory
from factories.user_factory import UserFactory
from domain.enums import City
from persistence.storage import (
    vehicles_exist,
    users_exist,
    load_vehicles,
    load_users,
    save_vehicles,
    save_users
)
import json
import os


def bootstrap_system():
    # ---- Vehicles ----
    if vehicles_exist():
        print("📦 Loading vehicles from disk")
        vehicles = load_vehicles()
    else:
        print("🚗 Creating vehicle fleet")
        vehicles = VehicleFactory.create_fleet(
            size=10_000,
            city_distribution={
                City.LONDON: 0.4,
                City.MILAN: 0.3,
                City.ROME: 0.3
            }
        )
        save_vehicles(vehicles)

    # ---- Users ----
    if users_exist():
        print("📦 Loading users from disk")
        users = load_users()
    else:
        print("👤 Creating users")
        users = UserFactory.create_users(2_000)
        save_users(users)

    return vehicles, users

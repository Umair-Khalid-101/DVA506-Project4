import json
import os
from domain.enums import VehicleType, City, VehicleState
from domain.vehicle import Vehicle
from domain.user import User

DATA_DIR = "data"
VEHICLE_PATH = f"{DATA_DIR}/vehicles.json"
USER_PATH = f"{DATA_DIR}/users.json"

def vehicles_exist() -> bool:
    return os.path.exists(VEHICLE_PATH)


def users_exist() -> bool:
    return os.path.exists(USER_PATH)


def load_vehicles() -> dict:
    with open(VEHICLE_PATH) as f:
        raw = json.load(f)

        vehicles = {}
    for vid, v in raw.items():
        vehicle = Vehicle(
            vehicle_id=v["id"],
            vtype=VehicleType(v["type"]),
            city=City(v["city"])
        )
        vehicle.state = VehicleState(v["state"])
        vehicles[vid] = vehicle

    return vehicles

def save_vehicles(vehicles: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(VEHICLE_PATH, "w") as f:
        json.dump(
            {
                vid: {
                    "id": v.id,
                    "type": v.type.value,
                    "city": v.city.value,
                    "state": v.state.value
                }
                for vid, v in vehicles.items()
            },
            f,
            indent=2
        )


def load_users() -> dict:
    with open(USER_PATH) as f:
        raw = json.load(f)

    return {
        uid: User(u["id"], u["name"])
        for uid, u in raw.items()
    }


def save_users(users: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USER_PATH, "w") as f:
        json.dump(
            {
                uid: {"id": u.id, "name": u.name}
                for uid, u in users.items()
            },
            f,
            indent=2
        )

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    with open(path) as f:
        return json.load(f)

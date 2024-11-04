from .conf import CLIENT_CONFIG_DIR, CLIENTS_DB_FILE
import os
import json


def load_clients():
    if os.path.exists(CLIENTS_DB_FILE):
        with open(CLIENTS_DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_clients(clients):
    os.makedirs(CLIENT_CONFIG_DIR, exist_ok=True)
    with open(CLIENTS_DB_FILE, "w") as f:
        json.dump(clients, f, indent=4)

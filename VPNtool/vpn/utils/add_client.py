from ..core.client import load_clients, save_clients
from ..core.utils import (
    create_client_config,
    generate_client_keys,
    add_client_to_server,
    update_server_config,
)
from ..core.ip_allocator import IPAllocator, load_existing_allocations
from ..core.conf import CLIENTS_DB_FILE, IP_POOL_FILE, START_IP, END_IP
from bson import ObjectId
from datetime import datetime
import pytz


def add_client(client_name,device_name):
    try:
        clients = load_clients()
        existing_allocations = load_existing_allocations(CLIENTS_DB_FILE)
        allocator = IPAllocator(
            START_IP, END_IP, IP_POOL_FILE, existing_allocations)

        client_ip = allocator.allocate_ip()

        # Creating space for new user
        if client_name not in clients:
            clients[client_name] = []

        # Start generating client details
        with open("/etc/wireguard/keys/server_public.key", "r") as spkf:
            server_public_key = spkf.read().strip()

        client_private_key, client_public_key = generate_client_keys(
            client_name)
        add_client_to_server(client_public_key, client_ip)
        update_server_config(client_public_key, client_ip)

        # Get current UTC datetime
        utc_now = datetime.now(pytz.utc)
        new = {
            # Generate an ObjectId and convert to string
            "id": str(ObjectId()),
            "deviceName": device_name,
            "ipAddress": client_ip,
            "clientPrivateKey": client_private_key,
            "clientPublicKey": client_public_key,
            "conf": create_client_config(
                client_private_key, server_public_key, client_ip
            ),
            "createdAt": utc_now.isoformat(),  # Convert datetime to ISO format string
        }
        # Load client config in clients.json
        clients[client_name].append(new)
        save_clients(clients)
        print(f"[*] VPN created successfully for {client_name} 🖧 🟢")
        print(new)
    except Exception as e:
        print(e)
        exit()

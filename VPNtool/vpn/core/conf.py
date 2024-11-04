import os
import ipaddress

KEYS_DIR = "/etc/wireguard/keys"
CLIENT_CONFIG_DIR = "/etc/wireguard/clients"
CLIENTS_DB_FILE = os.path.join(CLIENT_CONFIG_DIR, "clients.json")
IP_POOL_FILE = "/etc/wireguard/ip_pool.json"
SERVER_PRIVATE_KEY_FILE = os.path.join(KEYS_DIR, "server_private.key")
SERVER_PUBLIC_KEY_FILE = os.path.join(KEYS_DIR, "server_public.key")
WG_CONF_FILE = "/etc/wireguard/wg0.conf"

# Set start and end IP addresses for the pool
def calculate_ip_range(subnet):
    network = ipaddress.ip_network(subnet)
    start_ip = str(network.network_address + 2)
    end_ip = str(network.broadcast_address)
    return start_ip, end_ip

subnet = os.getenv("ALLOWED_IPS")
START_IP, END_IP = calculate_ip_range(subnet)
from ..core.conf import (
    KEYS_DIR,
    SERVER_PRIVATE_KEY_FILE,
    SERVER_PUBLIC_KEY_FILE,
    WG_CONF_FILE,
    CLIENTS_DB_FILE,
    IP_POOL_FILE,
    START_IP,
    END_IP,
)
import os
from ..core.utils import run_command
from ..core.ip_allocator import IPAllocator, load_existing_allocations


def start_vpn_configuration():
    # Check if the WireGuard configuration file already exists
    if os.path.exists(WG_CONF_FILE):
        print("[*] WireGuard configuration already exists. Skipping setup.⌛")
    else:
        # Starting configuration preparation
        print("[*] Preparing VPN setup 👾...")

        # Generate VPN keys if they do not exist
        if not os.path.exists(SERVER_PRIVATE_KEY_FILE) or not os.path.exists(
            SERVER_PUBLIC_KEY_FILE
        ):
            server_private_key = run_command(["wg", "genkey"])
            server_public_key = run_command(
                ["wg", "pubkey"], input_text=server_private_key
            )

            os.makedirs(KEYS_DIR, exist_ok=True)
            with open(SERVER_PRIVATE_KEY_FILE, "w") as private_key_file:
                private_key_file.write(server_private_key)
            with open(SERVER_PUBLIC_KEY_FILE, "w") as public_key_file:
                public_key_file.write(server_public_key)
        else:
            # Read existing VPN keys
            with open(SERVER_PRIVATE_KEY_FILE, "r") as private_key_file:
                server_private_key = private_key_file.read().strip()
            with open(SERVER_PUBLIC_KEY_FILE, "r") as public_key_file:
                server_public_key = public_key_file.read().strip()

        # Server configuration
        server_ip = os.getenv("SERVER_IP")
        server_port = os.getenv("SERVER_PORT")

        config = f"""[Interface]
PrivateKey = {server_private_key}
Address = {server_ip}
ListenPort = {server_port}
SaveConfig = true
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth+ -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth+ -j MASQUERADE
"""

        # Save the configuration file
        os.makedirs("/etc/wireguard", exist_ok=True)
        with open(WG_CONF_FILE, "w") as config_file:
            config_file.write(config)

        # Enable IP forwarding
        run_command(["sh", "-c", 'echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf'])
        run_command(["sysctl", "-p"])
        print("[*] Preparation done!! 🎯")

        try:
            run_command(["wg-quick", "up", "wg0"])
            print("[!] VPN now online 🟢")
        except Exception as e:
            if "already exists" in str(e):
                print("[*] VPN interface wg0 already exists. Skipping startup.")
            else:
                raise e

    # Generate IP pool if not exists
    existing_allocations = load_existing_allocations(CLIENTS_DB_FILE)
    allocator = IPAllocator(START_IP, END_IP, IP_POOL_FILE, existing_allocations)
    print("[*] IP pool generated and saved 🌐")

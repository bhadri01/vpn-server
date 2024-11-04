import subprocess
from .conf import WG_CONF_FILE
import os


def run_command(command, input_text=None):
    result = subprocess.run(
        command,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"Command {' '.join(command)} failed: {result.stderr}")
    return result.stdout.strip()


def create_client_config(client_private_key, server_public_key, client_ip):
    endpoint = os.getenv("ENDPOINT", "vpnstage.youngstorage.in")
    server_port = os.getenv("SERVER_PORT", "51820")
    allowed_ips = os.getenv("ALLOWED_IPS", "10.5.0.0/16")

    config = f"""[Interface]\nPrivateKey = {client_private_key}\nAddress = {client_ip}\n\n[Peer]\nPublicKey = {server_public_key}\nEndpoint = {endpoint}:{server_port}\nAllowedIPs = {allowed_ips}\nPersistentKeepalive = 30"""
    return config


def generate_client_keys(client_name):
    client_private_key = run_command(["wg", "genkey"])
    client_public_key = run_command(["wg", "pubkey"], input_text=client_private_key)

    return client_private_key, client_public_key


def add_client_to_server(client_public_key, client_ip):
    run_command(
        ["wg", "set", "wg0", "peer", client_public_key, "allowed-ips", client_ip]
    )


def update_server_config(client_public_key, client_ip):
    peer_config = f"""
[Peer]
PublicKey = {client_public_key}
AllowedIPs = {client_ip}
"""
    with open(WG_CONF_FILE, "a") as f:
        f.write(peer_config)
    run_command(["wg-quick", "save", "wg0"])


def remove_client_from_server(client_public_key):
    run_command(["wg", "set", "wg0", "peer", client_public_key, "remove"])


def remove_peer_from_conf(client_public_key):
    with open(WG_CONF_FILE, "r") as f:
        lines = f.readlines()

    with open(WG_CONF_FILE, "w") as f:
        skip = False
        for line in lines:
            if line.startswith("[Peer]"):
                if f"PublicKey = {client_public_key}" in line:
                    skip = True
                else:
                    skip = False
            if not skip:
                f.write(line)

    run_command(["wg-quick", "save", "wg0"])

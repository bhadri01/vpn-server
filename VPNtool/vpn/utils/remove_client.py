from ..core.client import load_clients, save_clients
from ..core.utils import remove_client_from_server, remove_peer_from_conf


def remove_client(client_name, client_ip):
    try:
        clients = load_clients()

        # Check if the client and VPN exist
        if client_name not in clients or client_ip not in [
            user["ipAddress"] for user in clients[client_name]
        ]:
            raise ValueError("[*] username and IP not found in VPN list ⭕")

        vpn_info, *_ = list(
            filter(lambda vpn: vpn["ipAddress"] ==
                   client_ip, clients[client_name])
        )

        client_public_key = vpn_info["clientPublicKey"]

        # # Remove the client from the server and configuration
        remove_client_from_server(client_public_key)
        remove_peer_from_conf(client_public_key)

        # # # Update the clients dictionary
        del clients[client_name][list(clients[client_name]).index(vpn_info)]

        # # Save the updated clients
        save_clients(clients)
        print(f"[*] VPN removed successfull for {client_name} 🖧 🟢")
        print(True)

    except Exception as e:
        print(e)
        print(False)
        exit()

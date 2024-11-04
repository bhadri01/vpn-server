from ..core.client import load_clients

clients = load_clients()


def show_ls():
    for index, client in enumerate(clients):
        print(f"[{index + 1}] - {client}")
    return clients


def show_username(username):
    try:
        if username not in clients:
            raise Exception("[*] Username not found in VPN list ⭕")
        print(f"[*] - {username}")
        for index, vpn in enumerate(clients[username]):
            print(f"[{index + 1}] - {vpn['ipAddress']}")
        return clients[username]
    except Exception as e:
        print(e)
        exit()


def show_username_ip_conf(username, ip):
    try:
        # Check if the client and VPN exist
        if username not in clients or ip not in [
            user["ipAddress"] for user in clients[username]
        ]:
            raise ValueError("[*] Username and IP not found in VPN list ⭕")

        vpn_info, * \
            _ = list(
                filter(lambda vpn: vpn["ipAddress"] == ip, clients[username]))

        print(f"{vpn_info['conf']}")
        return vpn_info
    except Exception as e:
        print(e)
        exit()

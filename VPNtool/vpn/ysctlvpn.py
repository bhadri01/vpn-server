#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
from .utils.start_vpn import start_vpn_configuration
from .utils.add_client import add_client
from .utils.remove_client import remove_client
from .utils.show import show_ls, show_username, show_username_ip_conf


def main():
    parser = argparse.ArgumentParser(
        prog="VPN",
        description="Youngstorage VPN management tool 🧰",
        epilog="Helps to connect everyone in private ⼛",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # start the vpn setup
    subparsers.add_parser("start", help="To start the VPN configuration")

    # add client setup
    add_client_parser = subparsers.add_parser("add", help="Add New client to VPN")
    add_client_parser.add_argument("username", type=str, help="Username to create VPN")
    add_client_parser.add_argument("device_name", type=str, help="device name to create VPN")

    # remove client setup
    remove_client_parser = subparsers.add_parser(
        "remove", help="Remove client from VPN"
    )
    remove_client_parser.add_argument(
        "username", type=str, help="Username to remove VPN"
    )
    remove_client_parser.add_argument("ip", type=str, help="IP to remove from the list")

    # show username VPN list
    show_parser = subparsers.add_parser("show", help="Show users VPN list")
    show_subparsers = show_parser.add_subparsers(
        dest="show_command", help="Show commands"
    )

    # `show ls` command
    show_subparsers.add_parser("ls", help="Show all users username in VPN")

    # `show username` command
    show_username_parser = show_subparsers.add_parser(
        "username", help="Show VPN list for a specific username"
    )
    show_username_parser.add_argument(
        "username", metavar="USERNAME", help="Username to show VPN list for"
    )

    # `show username ip` command
    show_username_ip_parser = show_subparsers.add_parser(
        "conf", help="Show VPN configuration for a specific username and IP"
    )
    show_username_ip_parser.add_argument(
        "username", metavar="USERNAME", help="Username to show VPN list for"
    )
    show_username_ip_parser.add_argument(
        "ip", metavar="IP", help="IP to show the VPN configuration for"
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.command == "start":
        start_vpn_configuration()
    elif args.command == "add":
        add_client(args.username, args.device_name)
    elif args.command == "remove":
        remove_client(args.username, args.ip)
    elif args.command == "show":
        if args.show_command == "ls":
            show_ls()
        elif args.show_command == "username":
            show_username(args.username)
        elif args.show_command == "conf":
            show_username_ip_conf(args.username, args.ip)
        else:
            show_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

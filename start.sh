#!/bin/sh

# Check if wg0.conf exists
if [ ! -f /etc/wireguard/wg0.conf ]; then
    # Run the ysctlvpn start command in the shell
    ysctlvpn start
else
    echo "[*] WireGuard configuration already exists. Skipping setup.⌛"
    wg-quick up wg0
    echo "[!] VPN now online 🟢"
fi

# Keep the script running
# cd /vpn/app && uvicorn main:app --host 0.0.0.0 --port 80
tail -f /dev/null



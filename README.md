# VPN Server

## Docker Setup

```
docker build -t vpn .
docker run -d --name vpn \
    -p 8000:8000 --cap-add=NET_ADMIN --cap-add=SYS_MODULE \
    -e ENDPOINT=vpn.youngstorage.in \
    -e SERVER_PORT=51820 \
    -e SERVER_IP=10.5.0.1/16 \
    -e ALLOWED_IPS=10.5.0.0/16 \
    vpn
```

## swarm mode

 create a overlay with or without attachable 
 ```
 docker network create --driver overlay --attachable vpn

 docker service create   --name client   --network vpn   --cap-add NET_ADMIN   --replicas 1   --constraint 'node.hostname == node1'   ubuntu bash -c "while true; do sleep 3600; done"

 ```

## AutoComplete setup
```
pip install -r requirements.txt
activate-global-python-argcomplete --user
chmod +x /vpn/VPNtool/vpn/ysctlvpn.py
eval "$(register-python-argcomplete /vpn/VPNtool/vpn/ysctlvpn.py)"
```
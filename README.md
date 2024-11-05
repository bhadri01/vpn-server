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

FROM python:3.11-alpine

RUN apk update && apk add --no-cache \
    wireguard-tools \
    iptables \
    iproute2 \
    git\
    bash \
    curl \
    jq 

COPY . /vpn

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /vpn/requirements.txt

RUN chmod +x /vpn/VPNtool/vpn/ysctlvpn.py 

RUN chmod +x /vpn/start.sh

CMD ["/vpn/start.sh"]


from fastapi import APIRouter, HTTPException
import subprocess
from fastapi import Depends
from routers.auth import get_current_user
from models.users import User
from typing import List, Dict, Any
import json
import os
import re

router = APIRouter()

commands = {
    "add": lambda username, device_name: f"ysctlvpn add {username} {device_name}",
    "remove": lambda username, ip: f"ysctlvpn remove {username} {ip}",
}


def read_clients_json() -> Dict[str, Any]:
    with open('/etc/wireguard/clients/clients.json', 'r') as file:
        return json.load(file)


def run_command(command):
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        stdout_lines = []
        stderr_lines = []

        while True:
            stdout_output = process.stdout.readline()
            stderr_output = process.stderr.readline()

            if stdout_output == "" and stderr_output == "" and process.poll() is not None:
                break

            if stdout_output:
                if stdout_output.strip().startswith("[*]"):
                    print(stdout_output.strip())
                else:
                    stdout_lines.append(stdout_output.strip())
            if stderr_output:
                stderr_lines.append(stderr_output.strip())

        return {"output": "\n".join(stdout_lines), "error": "\n".join(stderr_lines)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add/{username}/{device_name}")
async def add_user(username: str, device_name: str, current_user: dict = Depends(get_current_user)):
    command = commands["add"](username, device_name)
    result = run_command(command)

    if result["error"]:
        return {"message": "", "error": result["error"], "status": False}

    try:
        peer_data = eval(result["output"])  # Convert string to dictionary
        new_user = User(
            id=peer_data['id'],
            name=username,
            device_name=peer_data['name'],
            ip_address=peer_data['ipAddress'],
            client_private_key=peer_data['clientPrivateKey'],
            client_public_key=peer_data['clientPublicKey'],
            conf=peer_data['conf'],
            created_at=peer_data['createdAt']
        )
        return {"message": "User added successfully", "error": "", "status": True}
    except Exception as e:
        return {"message": "Failed to add user", "error": str(e), "status": False}


@router.delete("/remove/{username}/{ip}")
async def remove_user(username: str, ip: str, current_user: dict = Depends(get_current_user)):
    command = commands["remove"](username, ip)
    result = run_command(command)
    if result["error"]:
        return {"message": "", "error": result["error"], "status": False}
    else:
        return {"message": result["output"], "error": "", "status": True}


@router.get("/clients", response_model=List[str])
async def get_all_clients(current_user: dict = Depends(get_current_user)):
    try:
        clients = read_clients_json().keys()
        return {"message": clients, "error": "", "status": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{username}")
async def get_clients_by_username(username: str, current_user: dict = Depends(get_current_user)):
    try:
        clients = read_clients_json()
        if username in clients:
            return {"message": clients[username], "error": "", "status": True}
        else:
            raise HTTPException(status_code=404, detail="Username not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{username}/{id}")
async def get_clients_by_username_and_id(username: str, id: str, current_user: dict = Depends(get_current_user)):
    try:
        clients = read_clients_json()
        if username in clients:
            user_clients = clients[username]
            client_data = next(
                (client for client in user_clients if client['id'] == id), None)
            if client_data:
                return {"message": client_data, "error": "", "status": True}
            else:
                return {"message": "Client ID not found", "error": "", "status": True}
        else:
            raise HTTPException(status_code=404, detail="Username not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ping/{ip}")
async def ping_ip(ip: str, current_user: dict = Depends(get_current_user)):
    try:
        response = os.system(f"ping -c 1 {ip}")
        if response == 0:
            return {"message": f"{ip} is reachable", "error": "", "status": True}
        else:
            return {"message": f"{ip} is not reachable", "error": "", "status": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_peer_details(peer_key: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(['wg', 'show', 'all'],
                                capture_output=True, text=True)
        output = result.stdout

        # Regular expression to match the peer details
        peer_pattern = re.compile(
            rf"peer: {re.escape(peer_key)}\n"
            r"\s+endpoint: (?P<endpoint>.+)\n"
            r"\s+allowed ips: (?P<allowed_ips>.+)\n"
            r"\s+latest handshake: (?P<latest_handshake>.+)\n"
            r"\s+transfer: (?P<transfer_received>.+) received, (?P<transfer_sent>.+) sent"
        )

        match = peer_pattern.search(output)
        if match:
            return match.groupdict()
        else:
            raise ValueError("Peer not found")
    except Exception as e:
        raise ValueError(f"Error getting peer details: {str(e)}")


@router.get("/peer/{peer_key}", response_model=Dict[str, Any])
async def get_peer_info(peer_key: str, current_user: dict = Depends(get_current_user)):
    try:
        peer_details = get_peer_details(peer_key)
        return {"message": peer_details, "error": "", "status": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

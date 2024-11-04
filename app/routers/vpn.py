from fastapi import APIRouter, HTTPException
import subprocess

router = APIRouter()

commands = {
    "add": lambda username: f"ysctlvpn add {username}",
    "remove": lambda username, ip: f"ysctlvpn remove {username} {ip}",
    "listAll":"ysctlvpn show ls",
    "userList":lambda username : f"ysctlvpn show username {username}",
    "userConf": lambda username, ip: f"ysctlvpn show conf {username} {ip}",
}


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


@router.get("")
async def vpn():
    return {"message": "welcome to the vpn service"}


@router.post("/add/{username}")
async def add_user(username: str):
    command = commands["add"](username)
    result = run_command(command)
    return {"message": result["output"], "error": result["error"]}


@router.delete("/remove/{username}/{ip}")
async def remove_user(username: str, ip: str):
    command = commands["remove"](username, ip)
    result = run_command(command)
    return {"message": result["output"], "error": result["error"]}


@router.get("/userConf/{username}/{ip}")
async def show_conf(username: str, ip: str):
    command = commands["userConf"](username, ip)
    result = run_command(command)
    return {"message": result["output"], "error": result["error"]}

@router.get("/userList/{username}")
async def user_list(username: str):
    command = commands["userList"](username)
    result = run_command(command)
    data = str(result['output']).split('\n')
    userData = list(map(lambda x:x[6:],data))
    result['output'] = userData
    return result

@router.get("/listAll")
async def list_all():
    command = commands["listAll"]
    result = run_command(command)
    data = str(result['output']).split('\n')
    userData = list(map(lambda x:x[6:],data))
    result['output'] = userData
    return result
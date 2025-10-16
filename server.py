from flask import Flask, request, jsonify
import threading
import time
from advertiser import DeviceAdvertiser
from browser import Listener, Zeroconf, ServiceBrowser
from zeroconfMain import ZeroconfNode

app = Flask(__name__)

class ServerSide:
    """TCP handshake server managed using REST APIs"""
    def __init__(self):
        self.server_socket = None   # The server's TCP socket
        self.token = "admin"        # The server's access token (will be granted to the client after successful handshake)

    def accept_connection(self, public_key):
        """Parameters:
            public_key (str): public key provided by the client
           Returns:
           access_token (str): access token for future API calls"""
        
        try:
            # There will be a method to validate the public key
            # For now we will check if the public key is empty or not
            if not public_key:
                return {"code": 401, "message": "invalid public key"}
        
            return {
                "code": 201,
                "message": "Connection request accepted",
                "access_token": self.token
            }
        
        except Exception as e:
            return {"code": 500, "message": f"Error accepting connection: {str(e)}"}
        

server = ServerSide()

@app.route("/server/accept/", methods=["POST"])
def api_accept_connection():
    """Accept the connection by 
    sending the client its access token"""
    data = request.get_json()
    public_key = data.get("public_key")
    response = server.accept_connection(public_key)
    return jsonify(response), response["code"]

def run_server(host):
    thread = threading.Thread(target=lambda: app.run(host=host,port=8069,debug=False))
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    print("[+] Starting handshake server")
    # Plan: Start zeroconf, and whenever a service is discovered, start the handshake protocol,
    # Once the access token is successfully retreived, close zeroconf.
    # TLDR: Only start zeroconf when needed, otherwise keep it off.
    # Now the question is how do we get the IP and the port from zeroconf once it starts?
    node = ZeroconfNode("__master", 8069)
    run_server(node.ip)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.close()
    
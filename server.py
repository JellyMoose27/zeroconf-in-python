from flask import Flask, request, jsonify

import socket
import threading

app = Flask(__name__)

class ServerSide:
    """TCP handshake server managed using REST APIs"""
    def __init__(self):
        self.server_socket = None   # The server's TCP socket
        self.token = "admin"        # The server's access token (will be granted to the client after successful handshake)
        self.is_running = False     # The server's running status (to prevent from starting twice)
        self.listen_thread = None   # Thread that runs listening loop in the background
    
    def start_server(self, host="127.0.0.1", port=8069):
        """Opens a TCP socket, binds it to a port, and listens for incoming connections. 
           Calls socket.socket() > socket.binds() > socket.listen()"""
        
        if self.is_running:
            return {"code": 400, "message": "Server is already running!"}
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen()
            self.is_running = True

            print(f"Handshake server is now listening on {host}:{port}")
            return {"code": 200, "message": f"Server started and listening on {host}:{port}"}
        except Exception as e:
            # Catch socket errors
            return {"code": 500, "message": f"Failed to start server: {str(e)}"}
    
    def accept_connection(self, public_key):
        """Parameters:
            public_key (str): public key provided by the client
           Returns:
           access_token (str): access token for future API calls"""
        
        try:
            # There will be a method to validate the public key
            # For now we will check if the public key is empty or not
            if not self.is_running:
                return {"code": 403, "message": "Server is not running"}
            if not public_key:
                return {"code": 401, "message": "invalid public key"}
        
            return {
                "code": 201,
                "message": "Connection request accepted",
                "access_token": self.token
            }
        
        except Exception as e:
            return {"code": 500, "message": f"Error accepting connection: {str(e)}"}
        
    def close_connection(self):
        try:
            #set the running state to false
            self.is_running = False
            
            #close the server side's connection
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None

            return {
                "code": 205,
                "message": "Connection closed"
            }
        
        except Exception as e:
            return {
                "code": 500,
                "message": f"Error closing connection {str(e)}"
            }


server = ServerSide()

@app.route("/server/start/", methods=["POST"])
def api_start_server():
    """Start the server, the host and port will be default for now"""
    host = "127.0.0.1"
    port = 8069
    response = server.start_server(host, port)
    return jsonify(response), response["code"]

@app.route("/server/accept/", methods=["POST"])
def api_accept_connection():
    """Accept the connection by 
    sending the client its access token"""
    data = request.get_json()
    public_key = data.get("public_key")
    response = server.accept_connection(public_key)
    return jsonify(response), response["code"]

@app.route("/server/close/", methods=["DELETE"])
def api_close_connection():
    """Close the server"""
    response = server.close_connection()
    return jsonify(response), response["code"]

if __name__ == "__main__":
    # Host '0.0.0.0' allows access from any network interface
    app.run(host="0.0.0.0", port=5001, debug=True)
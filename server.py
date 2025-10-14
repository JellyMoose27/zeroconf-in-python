from flask import Flask, request, jsonify

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

if __name__ == "__main__":
    # Host '0.0.0.0' allows access from any network interface
    app.run(host="0.0.0.0", port=5001, debug=True)
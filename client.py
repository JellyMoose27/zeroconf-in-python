import socket
import threading
import requests
from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

app = Flask(__name__)

class ClientSide:
    """Send connection request to other devices"""
    def __init__(self):
        self.public_key = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
        self.access_token = None
        # self.is_connected = False

    def connect_to_server(self, host, port):
        """Perform a connection to the server
            And send its public key"""
        try:
            # self.is_connected = True

            print(f"Client connected to server {host}:{port}")

            pem_public_key = self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                          format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
            
            payload = {"public_key": pem_public_key}

            print("Sending request...")

            response = requests.post(f"http://{host}:{port}/server/accept/", json=payload)

            if response.status_code == 201:
                res_json = response.json()
                self.access_token = res_json.get("access_token")
                print("access token: ", self.access_token)
                print("Handshake successfully established")
                return {
                    "code": 200,
                    "message": "Sent public key successfully",
                    "access_token": self.access_token
                }
            else:
                print("Client handshake failed")
                return {
                    "code": 401,
                    "message": "Unauthorized: invalid public key"
                }
            
        except Exception as e:
            return {"code": 500, "message": f"Error attempting to connect: {str(e)}"}

client = ClientSide()

@app.route("/client/connect/", methods=["POST"])
def api_connect_to_server():
    data = request.get_json()
    server_host = data.get("server_host")
    server_port = data.get("server_port")

    response = client.connect_to_server(server_host, server_port)
    return jsonify(response), response["code"]

if __name__ == "__main__":
    """"""
    app.run(host="0.0.0.0", port=5002, debug=True)
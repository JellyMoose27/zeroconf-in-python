from flask import Flask, request, jsonify
import threading
import time
import requests
import json
import socket
from advertiser import DeviceAdvertiser
from browser import Listener, Zeroconf, ServiceBrowser
from zeroconfMain import ZeroconfNode
from datetime import datetime, timedelta, timezone
from functools import wraps
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt

SERVER_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
ALGORITHM = "RS256"
TOKEN_EXPIRATION_MINUTES = 30

ODOO_BASE_URL = "http://localhost:8069"

node = None

app = Flask(__name__)

class ServerSide:
    """TCP handshake server managed using REST APIs"""
    def __init__(self):
        self.server_socket = None   # The server's TCP socket
        self.client_token = {}
        
    def _issue_token(self, client_id):
        expiration = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        payload = {
            "client_id": client_id,
            "iat": datetime.now(timezone.utc),
            "exp": expiration,
        }
        token = jwt.encode(payload, SERVER_PRIVATE_KEY, algorithm=ALGORITHM)
        return token

    def accept_connection(self, public_key, device_host, device_port):
        """Parameters:
            public_key (str): public key provided by the client
        Returns:
        access_token (str): access token for future API calls"""
        
        try:
            # There will be a method to validate the public key
            # For now we will check if the public key is empty or not
            if not public_key:
                return {"code": 401, "message": "invalid public key"}
            
            client_id = "Client_" + str(hash(public_key))[:8]
            
            access_token = self._issue_token(client_id)
            self.client_token[client_id] = access_token
        
            payload = {
                "access_token": access_token,
                "device_host": device_host,
                "device_port": device_port,
            }

            odoo_url = ODOO_BASE_URL + "/api/v1/assign-token/device"

            response = requests.post(
                odoo_url,
                data = json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return {
                    "code": 201,
                    "message": "Connection request accepted",
                    "access_token": access_token
                }
            else:
                res_json = response.json()
                print(res_json.get('message'))
        
        except Exception as e:
            print(str(e))
            return {"code": 500, "message": f"Error accepting connection: {str(e)}"}


server = ServerSide()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        data = request.get_json()
        
        if 'access_token' in data:
            token = data['access_token']
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SERVER_PRIVATE_KEY, algorithms=[ALGORITHM])
            current_client_id = data['client_id']
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidSignatureError:
            return jsonify({'message': 'Token is invalid!'}), 403
        except Exception as e:
            return jsonify({'message': f'Token decode error: {str(e)}'}), 400

        return f(current_client_id, *args, **kwargs)

    return decorated

@app.route("/events/tag_entry/", methods=["POST"])
@token_required
def api_tag_entry_report(current_client_id):
    data = request.get_json()
    epc = data.get("epc")
    print(f"[SECURE REPORT] Tag {epc} reported by {current_client_id}")
    
    return jsonify({
        "code": 200,
        "message": "Event received and authenticated",
        "client_id": current_client_id
    }), 200

@app.route("/server/accept/", methods=["POST"])
def api_accept_connection():
    """Accept the connection by
    sending the client its access token
    Needs 3 parameters for input:
    public_key: the client's public key
    device_host: the client's IP address
    device_port: the client's port
    """
    data = request.get_json()
    public_key = data.get("public_key")
    device_host = data.get("device_host")
    device_port = data.get("device_port")
    response = server.accept_connection(public_key, device_host, device_port)
    return jsonify(response), response["code"]

def run_server(host):
    """Start the server using the ip address taken from the zeroconf"""
    thread = threading.Thread(target=lambda: app.run(host=host,port=8069,debug=False))
    thread.daemon = True
    thread.start()

@app.route("/server/start_discovery/", methods=["POST"])
def start_discovery():
    global node
    try:
        if node is not None:
            return jsonify({"code": 400, "message": "Zeroconf already running"}), 400
        
        service_name = request.json.get("service_name", "__master")
        port = request.json.get("port", 8069)

        node = ZeroconfNode(service_name, port)
        print(f"[+] Zeroconf discovery started on {service_name}:{port}")
        return jsonify({"code": 200, "message": "Discovery started successfully"}), 200

    except Exception as e:
        print(f"[!] Error starting discovery: {e}")
        return jsonify({"code": 500, "message": f"Error: {str(e)}"}), 500

@app.route("/server/stop_discovery/", methods=["POST"])
def stop_discovery():
    global node
    try:
        if node is None:
            return jsonify({"code": 404, "message": "No active discovery session"}), 404

        node.close()
        node = None
        print("[x] Zeroconf stopped")
        return jsonify({"code": 200, "message": "Zeroconf stopped successfully"}), 200

    except Exception as e:
        return jsonify({"code": 500, "message": f"Error stopping discovery: {str(e)}"}), 500

def _get_lan_ip():
        """return LAM IP address of the current machine (server)"""
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(("8.8.8.8",80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

if __name__ == "__main__":
    print("[+] Starting handshake server")
    # Plan: Start zeroconf, and whenever a service is discovered, start the handshake protocol,
    # Once the access token is successfully retreived, close zeroconf.
    # TLDR: Only start zeroconf when needed, otherwise keep it off.
    # Now the question is how do we get the IP and the port from zeroconf once it starts?
    
    lan_ip = _get_lan_ip()

    run_server(lan_ip)

    print(f"Server now running on {lan_ip}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("stopped waiting")
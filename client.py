import socket

class HandshakeClient:
    def __init__(self, token="admin"):
        self.token = token

    def perform(self, ip, port):
        try:
            sock = socket.create_connection((ip, port), timeout=5)
            sock.sendall(self.token.encode("utf-8") + b"\n")
            response = sock.recv(1024).decode("utf-8").strip()
            sock.close()
            if response == "OK":
                print(f"Handshake success with {ip}:{port} ✅")
                return True
            else:
                print(f"Handshake failed with {ip}:{port} ❌")
                return False
        except Exception as e:
            print(f"Error during handshake: {e}")
            return False

if __name__ == "__main__":
    client = HandshakeClient(token="admin")
    client.perform("127.0.0.1", port=9090)
import socket
import threading

class Handshake:
    def __init__(self, host, port=8069, token="admin"):
        self.host, self.port = (host, port)
        self.token = token
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Handshake listening on port {self.port}")
    
    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"[HandshakeServer] Connection from {addr}")
            t = threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True)
            t.start()
    
    def _handle_client(self, socket):
        try:
            data = socket.recv(1024).decode("utf-8").strip()
            if data == self.token:
                socket.sendall(b"OK\n")
                print("[HandshakeServer] Handshake success ✅")
            else:
                socket.sendall(b"FAIL\n")
                print("[HandshakeServer] Handshake failed ❌")
        except Exception as e:
            print(f"[HandshakeServer] Error: {e}")
        finally:
            socket.close()

if __name__ == "__main__":
    server = Handshake("0.0.0.0" ,port=9090, token="admin")
    server.start()
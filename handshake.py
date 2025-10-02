import socket
import threading

class Handshake:
    def __init__(self, host="0.0.0.0", port=9000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        print(f"[+] Handshake listening on {self.host}:{self.port}")

    def start(self):
        threading.Thread(target=self.accept_loop, daemon=True).start()
    
    def accept_loop(self):
        while True:
            client, addr = self.server.accept()
            print(f"[+] Incoming handshake from {addr}")
            data = client.recv(1024).decode()
            print(f"Received: {data}")
            client.send(b"HELLO_ACK")
            client.close()

if __name__ == "__main__":
    print("Please enter the IP adddress and Port to connect to")
    ip = input("IP Address: ")
    port = input("Port: ")
    handshake = Handshake(ip,port)

    
from zeroconf import *
import socket

class Listener(ServiceListener):
    """Browser"""
    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            addresses = [addr for addr in info.parsed_addresses()]
            print(f"[+] Service discovered: {name}")
            print(f"    Address: {addresses}")
            print(f"    Port: {info.port}")
            print(f"    Properties: {info.properties}")
            self.connect_to_controller(addresses[0], info.port)
        else:
            print(f"[+] Service discovered: {name} (no info yet)")

    def update_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            ip = info.parsed_addresses()[0] if info.parsed_addresses() else None
            print(f"[UPDATED] {name} changed -> {ip}:{info.port} - {info.properties}\n")

    def connect_to_controller(self, ip, port):
        """Kết nối TCP tới controller và nhận dữ liệu"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, port))
                print(f"[Listener] Connected to controller {ip}:{port}")
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    print("[Listener] Received:", data.decode())
            except Exception as e:
                print("[Listener] Error:", e)

    def remove_service(self, zc, type_, name):
        print(f"Service {name} removed: service went offline")
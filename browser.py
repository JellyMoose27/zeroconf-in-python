from zeroconf import *
import socket
import threading

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
        else:
            print(f"[+] Service discovered: {name} (no info yet)")

    def update_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            ip = info.parsed_addresses()[0] if info.parsed_addresses() else None
            print(f"[UPDATED] {name} changed -> {ip}:{info.port} - {info.properties}\n")

    def remove_service(self, zc, type_, name):
        print(f"Service {name} removed: service went offline")
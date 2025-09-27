from zeroconf import *
import time
import threading

class Listener(ServiceListener):
    """Browser"""
    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            ip = info.parsed_addresses()[0] if info.parsed_addresses() else None
            print(f"Discovered: {name} @ {ip}:{info.port} - {info.properties}\n")

    def update_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info:
            ip = info.parsed_addresses()[0] if info.parsed_addresses() else None
            print(f"[UPDATED] {name} changed -> {ip}:{info.port} - {info.properties}\n")

    def remove_service(self, zc, type_, name):
        print(f"Service {name} removed: service went offline")

zeroconf = Zeroconf()
listener = Listener()
browser = ServiceBrowser(zeroconf, "_odoo._tcp.local.", listener)

try:
    input("Browser is running! Now every service discovered will be displayed here.\n Press enter to exit\n")
finally:
    zeroconf.close()
import threading
import time

from advertiser import DeviceAdvertiser
from browser import Listener, Zeroconf, ServiceBrowser
from handshake import Handshake

class ZeroconfNode:
    def __init__(self, service_name="Odoo_Local", port=8069):
        self.advertiser = DeviceAdvertiser(service_name, port)
        self.advertiser.register()

        self.zeroconf = Zeroconf()
        self.listener = Listener()
        self.browser = ServiceBrowser(self.zeroconf, "_odoo._tcp.local.", self.listener)

    def close(self):
        print("[x] Shutting down Zeroconf...")
        self.advertiser.unregister()
        self.zeroconf.close()

if __name__ == "__main__":
    while True:
        print("\n--- Zeroconf Menu ---")
        print("1. Start Service")
        print("2. Exit")

        choice = input("Your choice: ")
        if choice == "1":
            node = ZeroconfNode("nsp_controller", 8069)
            try:
                print("ZeroconfNode running. Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                node.close()
                print("\n[X] Zeroconf stopped returning to menu...")
        elif choice == "2":
            print("[X] Exiting...")
            break
        else:
            print("[X] Invalid choice")
    
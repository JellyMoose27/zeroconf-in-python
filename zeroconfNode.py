import threading
import time

from advertiser import DeviceAdvertiser
from browser import Listener, Zeroconf, ServiceBrowser

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
    node = ZeroconfNode("nsp_controller", 8069)

    try:
        print("ZeroconfNode running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.close()

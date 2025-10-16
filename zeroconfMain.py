from advertiser import DeviceAdvertiser
from browser import Listener, Zeroconf, ServiceBrowser

class ZeroconfNode:
    def __init__(self, service_name, port=8069):
        self.advertiser = DeviceAdvertiser(service_name, port)
        self.ip = self.advertiser.get_ip()
        self.advertiser.register() #Advertise onto the network

        self.zeroconf = Zeroconf()
        self.listener = Listener() #start browsing for services
        self.browser = ServiceBrowser(self.zeroconf, "_nsp._tcp.local.", self.listener)

    def close(self):
        print("[x] Shutting down Zeroconf...")
        self.advertiser.unregister()
        self.zeroconf.close()
    
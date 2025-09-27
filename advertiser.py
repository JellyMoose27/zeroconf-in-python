from zeroconf import *
import socket

class DeviceAdvertiser:
    def __init__(self, service_name="Odoo", port=8069):
        self.zeroconf = Zeroconf()
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)

        self.info = ServiceInfo(
            type_="_odoo._tcp.local.",
            name=f"{service_name}._odoo._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=port,
            properties={"version": "18.0"},
            server=f"{hostname}.local."
        )

    def register(self):
        print("Registering service...")
        self.zeroconf.register_service(self.info)
    
    def unregister(self):
        print("Unregistering service...")
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

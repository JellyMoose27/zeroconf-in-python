from zeroconf import *
import socket

class DeviceAdvertiser:
    def __init__(self, service_name="Odoo", port=8069):
        self.zeroconf = Zeroconf()
        hostname = socket.gethostname()
        self.ip = self._get_lan_ip()

        self.info = ServiceInfo(
            type_="_nsp._tcp.local.",
            name=f"{service_name}._nsp._tcp.local.",
            addresses=[socket.inet_aton(self.ip)],
            port=port,
            properties={"version": "18.0"},
            server=f"{hostname}.local."
        )

    def _get_lan_ip(self):
        """return LAM IP address of the current machine (server)"""
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(("8.8.8.8",80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_ip(self):
        return self.ip
    
    def register(self):
        print("Registering service...")
        self.zeroconf.register_service(self.info, allow_name_change=True)
    
    def unregister(self):
        print("Unregistering service...")
        self.zeroconf.unregister_service(self.info)
        self.zeroconf.close()

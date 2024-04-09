from netunicorn.base import Task


class PortKnock(Task):
    def __init__(self, ip: str, port: int, *args, **kwargs):
        self.ip = ip
        self.port = port
        super().__init__(*args, **kwargs)

    def run(self):
        import socket

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.port))
            s.close()
        except Exception:
            pass

        return 0

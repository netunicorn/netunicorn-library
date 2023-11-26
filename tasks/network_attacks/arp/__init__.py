from netunicorn.base.task import Task

from .spoof import main


class ArpSpoof(Task):
    def __init__(
        self,
        target_ip: str,
        spoof_ip: str,
        interface: str = "eth0",
        duration_seconds: int = 60,
        *args,
        **kwargs
    ):
        self.target_ip = target_ip
        self.spoof_ip = spoof_ip
        self.interface = interface
        self.duration_seconds = duration_seconds
        super().__init__(*args, **kwargs)

    def run(self):
        return main(
            self.target_ip, self.spoof_ip, self.interface, self.duration_seconds
        )

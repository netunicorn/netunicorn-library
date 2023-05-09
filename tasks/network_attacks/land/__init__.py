from netunicorn.base.task import Task
from .landattack import land_attack


class LANDAttack(Task):
    requirements = ["pip install scapy"]

    def __init__(
        self, target_ip: str, source_port: int = 1001, destination_port: int = 80
    ):
        self.target_ip = target_ip
        self.source_port = source_port
        self.destination_port = destination_port
        super().__init__()

    def run(self):
        return land_attack(self.target_ip, self.source_port, self.destination_port)

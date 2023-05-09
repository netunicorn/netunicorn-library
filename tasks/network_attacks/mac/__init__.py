from netunicorn.base.task import Task
from .flooder import flood


class MACFlooder(Task):
    def __init__(self, iface: str = "eth0", count: int = 1000):
        self.iface = iface
        self.count = count
        super().__init__()

    def run(self):
        return flood(self.iface, self.count)

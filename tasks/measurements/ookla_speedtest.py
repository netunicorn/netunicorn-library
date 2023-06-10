import subprocess
from typing import Dict

from netunicorn.base.architecture import Architecture
from netunicorn.base.nodes import Node
from netunicorn.base.task import Failure, Task, TaskDispatcher


class SpeedTest(TaskDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_instance = SpeedTestLinuxImplementation(name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_instance

        raise NotImplementedError(
            f'SpeedTest is not implemented for architecture: {node.architecture}'
        )


class SpeedTestLinuxImplementation(Task):
    requirements = ["pip install speedtest-cli"]

    def run(self):
        result = subprocess.run(["speedtest-cli", "--simple", "--secure"], capture_output=True)
        if result.returncode != 0:
            return Failure(
                result.stdout.decode("utf-8").strip()
                + "\n"
                + result.stderr.decode("utf-8").strip()
            )

        return self._format_data(result.stdout.decode("utf-8"))

    @staticmethod
    def _format_data(data: str) -> Dict[str, Dict]:
        ping, download, upload, _ = data.split("\n")
        return {
            "ping": {"value": float(ping.split(" ")[1]), "unit": ping.split(" ")[2]},
            "download": {
                "value": float(download.split(" ")[1]),
                "unit": download.split(" ")[2],
            },
            "upload": {
                "value": float(upload.split(" ")[1]),
                "unit": upload.split(" ")[2],
            },
        }

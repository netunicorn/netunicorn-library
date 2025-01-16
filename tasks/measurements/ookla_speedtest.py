import typing
import subprocess
import json

from netunicorn.base import Architecture, Node, Task, TaskDispatcher
from netunicorn.library.tasks.tasks_utils import subprocess_run


class SpeedTest(TaskDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_instance = SpeedTestLinuxImplementation(name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_instance

        raise NotImplementedError(
            f"SpeedTest is not implemented for architecture: {node.architecture}"
        )


class SpeedTestLinuxImplementation(Task):
    requirements = ["pip install speedtest-cli"]

    def run(self):
        return subprocess_run(["speedtest-cli", "--simple", "--secure"]).map(
            self._format_data
        )

    @staticmethod
    def _format_data(data: str) -> Dict[str, Dict]:
        ping, download, upload, *other = data.split("\n")
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
            "other": other,
        }


class Server_Info(typing.TypedDict):
    id: int
    host: str
    port: int
    name: str
    location: str
    country: str

class Server_Selection(Task):
    def __init__(self, callback: typing.Callable[[list[Server_Info]], int] , *args, **kwargs):
        self.callback = callback
        super().__init__(*args, **kwargs)
    
    def run(self):
        flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--servers", "--format=json"]
        result = subprocess.run(["speedtest"] + flags, stdout=subprocess.PIPE)
        if result.returncode == 0:
            servers = json.loads(result.stdout.decode())["servers"]
            return {"server_id": self.callback(servers)}
        else:
            return Failure("Failed somehow") # todo: fix error msg
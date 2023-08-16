import subprocess
from typing import List, Optional

from netunicorn.base import Task


class StartServer(Task):
    """
    Starts netserver on the node.
    """

    requirements = ["sudo apt install netperf"]

    def run(self) -> str:
        return subprocess.check_output(["netserver"]).decode("utf-8")


class StopServer(Task):
    """
    Stops all netservers on the node.
    """

    def run(self) -> str:
        return subprocess.check_output(["killall", "netserver"]).decode("utf-8")


class FlentCommand(Task):
    requirements = [
        "sudo apt install -y netperf iputils-ping irtt python3-pip",
        "pip install matplotlib flent",
    ]

    def __init__(
            self,
            test_name: str = "rrul",
            host: str = "netperf-west.bufferbloat.net",
            duration: int = 60,
            additional_arguments: Optional[List[str]] = None,
            *args,
            **kwargs,
    ):
        self.test_name = test_name
        self.host = host
        self.duration = duration
        self.additional_arguments = additional_arguments or []
        super().__init__(*args, **kwargs)

    def run(self) -> str:
        command = ["flent", self.test_name, "-H", self.host, "-l", str(self.duration)]
        command.extend(self.additional_arguments)
        return subprocess.check_output(command).decode("utf-8")


class PingTest(FlentCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(test_name="ping", *args, **kwargs)


class CubicBBRTest(FlentCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(test_name="cubic_bbr", *args, **kwargs)


class RRULTest(FlentCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(test_name="rrul", *args, **kwargs)


class TCPDownloadTest(FlentCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(test_name="tcp_download", *args, **kwargs)


class TCPUploadTest(FlentCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(test_name="tcp_upload", *args, **kwargs)


class VOIPTest(FlentCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(test_name="voip", *args, **kwargs)

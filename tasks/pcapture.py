import subprocess
import time
import signal
from typing import List, Optional

from netunicorn.base.nodes import Node
from netunicorn.base.task import Failure, Task, TaskDispatcher


class StartCapture(TaskDispatcher):
    def __init__(self, filepath: str, arguments: Optional[List[str]] = None):
        self.filepath = filepath
        self.arguments = arguments
        super().__init__()

    def dispatch(self, node: Node) -> Task:
        if node.properties.get("os_family", "").lower() == "linux":
            return StartCaptureLinuxImplementation(self.filepath, self.arguments)

        raise NotImplementedError(
            f'StartCapture is not implemented for {node.properties.get("os_family", "")}'
        )


class StartCaptureLinuxImplementation(Task):
    requirements = ["sudo apt-get update", "sudo apt-get install -y tcpdump"]

    def __init__(self, filepath: str, arguments: Optional[List[str]] = None):
        self.arguments = arguments or []
        self.filepath = filepath
        super().__init__()

    def run(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        proc = subprocess.Popen(
            ["tcpdump"] + self.arguments + ["-U", "-w", self.filepath]
        )
        time.sleep(2)
        if (exit_code := proc.poll()) is None:
            return (
                f"Successfully started tcpdump with filepath={self.filepath}, "
                f"additional arguments: {self.arguments}, "
                f"process ID: {proc.pid}"
            )

        return Failure(f"Tcpdump terminated with return code {exit_code}")


class StopAllTCPDumps(TaskDispatcher):
    def dispatch(self, node: Node) -> Task:
        if node.properties.get("os_family", "").lower() == "linux":
            return StopAllTCPDumpsLinuxImplementation()

        raise NotImplementedError(
            f'StopAllTCPDumps is not implemented for {node.properties.get("os_family", "")}'
        )


class StopAllTCPDumpsLinuxImplementation(Task):
    def run(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        subprocess.Popen(
            ["killall", "-w", "tcpdump"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return "Successfully killed all tcpdump processes"

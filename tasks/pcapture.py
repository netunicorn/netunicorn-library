import subprocess
import time
import signal
from typing import List, Optional

from netunicorn.base.architecture import Architecture
from netunicorn.base.nodes import Node
from netunicorn.base import Task, TaskDispatcher, Result, Success, Failure


class StartCapture(TaskDispatcher):
    def __init__(self, filepath: str, arguments: Optional[List[str]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filepath = filepath
        self.arguments = arguments
        self.args = args
        self.kwargs = kwargs

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return StartCaptureLinuxImplementation(filepath=self.filepath, arguments=self.arguments, *self.args,
                                                   **self.kwargs)

        raise NotImplementedError(
            f'StartCapture is not implemented for {node.architecture}'
        )


class StartCaptureLinuxImplementation(Task):
    requirements = ["sudo apt-get update", "sudo apt-get install -y tcpdump"]

    def __init__(self, filepath: str, arguments: Optional[List[str]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arguments = arguments or []
        self.filepath = filepath

    def run(self) -> Result:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

        proc = subprocess.Popen(
            ["tcpdump"] + self.arguments + ["-U", "-w", self.filepath]
        )
        time.sleep(2)
        if (exit_code := proc.poll()) is None:  # not finished yet
            return Success(proc.pid)
        return Failure(f"Tcpdump terminated with return code {exit_code}")


class StopNamedCapture(TaskDispatcher):
    def __init__(self, start_capture_task_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.start_capture_task_name = start_capture_task_name

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return StopNamedCaptureLinuxImplementation(
                *self.args,
                capture_task_name=self.start_capture_task_name,
                **self.kwargs,
            )

        raise NotImplementedError(
            f'StopCapture is not implemented for {node.architecture}'
        )


class StopNamedCaptureLinuxImplementation(Task):
    def __init__(self, capture_task_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capture_task_name = capture_task_name

    def run(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        pid = self.previous_steps.get(self.capture_task_name, [Failure("Named StartCapture not found")])[-1]
        if isinstance(pid, Failure):
            return pid

        pid = pid.unwrap()
        return subprocess.check_output(["kill", str(pid)])


class StopAllTCPDumps(TaskDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return StopAllTCPDumpsLinuxImplementation(*self.args, **self.kwargs)

        raise NotImplementedError(
            f'StopAllTCPDumps is not implemented for {node.architecture}'
        )


class StopAllTCPDumpsLinuxImplementation(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        subprocess.Popen(
            ["killall", "-w", "tcpdump"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return "Successfully killed all tcpdump processes"

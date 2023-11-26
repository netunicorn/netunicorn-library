import subprocess
import time
from typing import Optional

from netunicorn.base import Failure, Success, Task
from netunicorn.library.tasks.tasks_utils import subprocess_run


class Iperf3ServerStart(Task):
    requirements = ["apt-get install -y iperf3"]

    def __init__(self, flags: Optional[list[str]] = None, *args, **kwargs):
        self.flags = flags or []
        if "-s" not in self.flags:
            self.flags += ["-s"]
        super().__init__(*args, **kwargs)

    def run(self) -> str:
        process = subprocess.Popen(
            ["iperf3"] + self.flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(2)
        if process.poll() is None:  # not finished yet
            return Success(process.pid)

        text = ""
        if process.stdout:
            text = process.stdout.read().decode("utf-8") + "\n"
        if process.stderr:
            text += process.stderr.read().decode("utf-8")
        return Failure(text)


class Iperf3ServerStop(Task):
    """
    This task stops a iperf3 server.
    If task name is provided, the pid of the process is retrieved from the task.
    Otherwise, killall is used.
    """

    requirements = ["apt-get install -y procps"]

    def __init__(
        self, iperf3_server_start_task_name: Optional[str] = None, *args, **kwargs
    ):
        self.iperf3_server_start_task_name = iperf3_server_start_task_name
        super().__init__(*args, **kwargs)

    def run(self) -> str:
        if self.iperf3_server_start_task_name is None:
            return subprocess_run(["killall", "iperf3"])

        pid = self.previous_steps.get(
            self.iperf3_server_start_task_name,
            [Failure("Named StartCapture not found")],
        )[-1]

        if isinstance(pid, Failure):
            return pid

        return subprocess_run(["kill", str(pid.unwrap())])


class Iperf3Client(Task):
    """
    This task runs a iperf3 client.
    There must be a '-c <server_ip>' flag.
    """

    requirements = ["apt-get install -y iperf3"]

    def __init__(self, flags: list[str], *args, **kwargs):
        if not any(flag.startswith("-c") for flag in flags):
            raise ValueError("No server ip specified")

        self.flags = flags
        super().__init__(*args, **kwargs)

    def run(self) -> str:
        return subprocess_run(["iperf3"] + self.flags)

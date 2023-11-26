from typing import Optional

from netunicorn.base import Architecture, Node, Task, TaskDispatcher
from netunicorn.library.tasks.tasks_utils import subprocess_run

__all__ = [
    "NDT7SpeedTest",
    "NDT7SpeedTestLinuxAMD64",
    "NDT7SpeedTestLinuxARM64",
]


class _NDTSpeedTestImplementation(Task):
    def __init__(
        self,
        flags: Optional[list[str]] = None,
        source_ip: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.flags = flags or ["-format", "json"]
        if source_ip:
            self.flags += ["-source", f"{source_ip}"]
        super().__init__(*args, **kwargs)

    def run(self) -> str:
        return subprocess_run(["ndt7-client"] + self.flags)


class NDT7SpeedTestLinuxAMD64(_NDTSpeedTestImplementation):
    requirements = [
        "apt update && apt install -y wget",
        "wget https://github.com/netunicorn/netunicorn-library/releases/download/ndt7-client-0.1/ndt7-client-linux-amd64 -O /bin/ndt7-client",
        "chmod +x /bin/ndt7-client",
    ]


class NDT7SpeedTestLinuxARM64(_NDTSpeedTestImplementation):
    requirements = [
        "apt update && apt install -y wget",
        "wget https://github.com/netunicorn/netunicorn-library/releases/download/ndt7-client-0.1/ndt7-client-linux-arm64 -O /bin/ndt7-client",
        "chmod +x /bin/ndt7-client",
    ]


class NDT7SpeedTest(TaskDispatcher):
    def __init__(
        self,
        source_ip: Optional[str] = None,
        flags: Optional[list[str]] = None,
        *args,
        **kwargs,
    ):
        self.amd64_task = NDT7SpeedTestLinuxAMD64(flags=flags, source_ip=source_ip)
        self.arm64_task = NDT7SpeedTestLinuxARM64(flags=flags, source_ip=source_ip)
        super().__init__(*args, **kwargs)

    def dispatch(self, node: Node) -> Task:
        if node.architecture == Architecture.LINUX_ARM64:
            return self.arm64_task
        elif node.architecture == Architecture.LINUX_AMD64:
            return self.amd64_task
        else:
            raise Exception(
                f"NDT7 speed test is not supported for {node.architecture} architecture"
            )

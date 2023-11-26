from abc import ABC
from typing import Optional

from netunicorn.base import Architecture, Node, Result, Task, TaskDispatcher
from netunicorn.library.tasks.tasks_utils import subprocess_run


class _ZeekDebian12(Task, ABC):
    """
    Only for Debian 12 (bookworm)
    """

    requirements = [
        "apt-get install -y curl",
        "echo 'deb http://download.opensuse.org/repositories/security:/zeek/Debian_12/ /' | sudo tee /etc/apt/sources.list.d/security:zeek.list",
        "curl -fsSL https://download.opensuse.org/repositories/security:zeek/Debian_12/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null",
        "sudo apt-get update",
        "sudo apt-get install -y zeek-6.0",
    ]


class ZeekPCAPAnalysisLinuxImplementation(Task):
    def __init__(
        self, pcap_filename: str, flags: Optional[list[str]] = None, *args, **kwargs
    ):
        self.flags = flags or []
        self.pcap_filename = pcap_filename
        super().__init__(*args, **kwargs)

    def run(self) -> Result:
        return subprocess_run(
            ["/opt/zeek/bin/zeek"] + self.flags + ["-r", self.pcap_filename]
        )


class ZeekPCAPAnalysis(TaskDispatcher):
    def __init__(
        self, pcap_filename: str, flags: Optional[list[str]] = None, *args, **kwargs
    ):
        self.linux_debian_implementation = ZeekPCAPAnalysisLinuxImplementation(
            pcap_filename=pcap_filename, flags=flags
        )
        super().__init__(*args, **kwargs)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_debian_implementation
        else:
            raise NotImplementedError(
                f"Architecture {node.architecture} is not supported for ZeekPCAPAnalysis"
            )

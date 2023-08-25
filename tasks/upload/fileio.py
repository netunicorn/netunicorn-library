"""
Uploads files to file.io -- temporary file storage
"""

import subprocess

from netunicorn.base.nodes import Architecture, Node
from netunicorn.base.task import Task, TaskDispatcher


class UploadToFileIO(TaskDispatcher):
    def __init__(self, filepath: str, expires: str = "14d", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_implementation = UploadToFileIOCurlImplementation(
            filepath=filepath, expires=expires, name=self.name
        )
        self.linux_implementation.requirements = ["sudo apt-get install -y curl"]

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation

        raise NotImplementedError(
            f"UploadToFileIO is not implemented for architecture: {node.architecture}"
        )


class UploadToFileIOCurlImplementation(Task):
    def __init__(self, filepath: str, expires: str = "14d", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filepath = filepath
        self.expires = expires

    def run(self):
        command = ["curl", "-F", f"file=@{self.filepath}", f"https://file.io?expires={self.expires}"]
        return subprocess.run(command, check=True, capture_output=True).stdout.decode("utf-8")



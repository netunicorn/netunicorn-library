import time
import subprocess
from subprocess import Popen
import os
import logging
import subprocess
import time
from netunicorn.base.architecture import Architecture # type: ignore
from netunicorn.base.nodes import Node # type: ignore
from netunicorn.base.task import Failure, Task, TaskDispatcher # type: ignore
from netunicorn.client.remote import RemoteClient, RemoteClientException # type: ignore
from netunicorn.base import Experiment, ExperimentStatus, Pipeline # type: ignore
from netunicorn.library.tasks.basic import ShellCommand # type: ignore
from netunicorn.base.architecture import Architecture # type: ignore
from netunicorn.base.nodes import Node # type: ignore
from netunicorn.base.task import Failure, Task, TaskDispatcher # type: ignore
from netunicorn.base import Result, Failure, Success, Task, TaskDispatcher # type: ignore
from netunicorn.base.architecture import Architecture # type: ignore
from netunicorn.base.nodes import Node # type: ignore
from returns.pipeline import is_successful # type: ignore
from returns.result import Failure # type: ignore

class Ookla_Speedtest_CLI(TaskDispatcher):
    def __init__(self, filepath: str, server: str = '', ip: str = '', timeout: int = 120, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_implementation = Ookla_Speedtest_CLI_LinuxImplementation(
            filepath=filepath, timeout=timeout, server=server, ip=ip, name=self.name
        )

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ookla_Speedtest_CLI is not implemented for architecture: {node.architecture}"
        )
    
class Ookla_Speedtest_CLI_LinuxImplementation(Task):
    def __init__(self, filepath: str, server: str = '', ip: str = '', timeout: int = 120, *args, **kwargs):
        self.filepath = filepath
        self.timeout = timeout
        self.server = server
        self.ip = ip
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            with open(self.filepath, 'w') as outfile:
                flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--format=json", "-v"]
                if self.server != '':
                    flags.append(f"--server-id={self.server}")
                if self.ip != '':
                    flags.append(f"--ip={self.ip}")
                result = subprocess.run(
                    ["speedtest"] + flags,
                    stdout=outfile,
                    stderr=outfile,
                    timeout=self.timeout
                )
            result = subprocess.run(["cat", self.filepath], capture_output = True)
            if result.returncode == 0:
                return Success({"test_result" : result.stdout.decode("utf8")})
            else:
                return Failure(f"Ookla_Speedtest_CLI failed with return code {result.returncode}, Error: {result.stdout.decode("utf-8").strip()}\n{result.stderr.decode("utf-8").strip()}")
        except subprocess.TimeoutExpired:
            return Failure("Ookla_Speedtest_CLI timed out.")
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    cli_task = Ookla_Speedtest_CLI(filepath="ookla_cli_results.json", name="Ookla CLI Speedtest")
    print(cli_task.run())
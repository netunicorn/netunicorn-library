import subprocess
import json
from typing import Callable

from netunicorn.base import Architecture, Failure, Success, Task, TaskDispatcher, Node
from subprocess import CalledProcessError
from dataclasses import dataclass

UNIX_REQUIREMENTS = [
    "apt-get install curl --yes",
    "curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash",
    "apt-get install speedtest --yes",
]

@dataclass
class SpeedTestOptions:
    server_selection_task_name: str = ""
    server_ip: str = ""
    timeout: int = 100

@dataclass
class ServerInfo:
    id: int
    host: str
    port: int
    name: str
    location: str
    country: str

class OoklaSpeedtest(TaskDispatcher):
    def __init__(self, options: SpeedTestOptions = SpeedTestOptions(), *args, **kwargs):
        """
        Use `SpeedTestOptions` to proivde either `server_selection_task_name` or `server_ip` to ping to a certain server.
        If neither are provided, a server will be automatically selected.
        If both are proived, the server id from the server selection task will be prioritized.

        Additionally, the `timeout` time can be specify using `SpeedTestOptions`
        """
        super().__init__(*args, **kwargs)
        self.linux_implementation = OoklaSpeedtestLinuxImplementation(options, name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ookla Speedtest is not implemented for architecture: {node.architecture}"
        )
    
class OoklaSpeedtestLinuxImplementation(Task):
    requirements = UNIX_REQUIREMENTS

    def __init__(self, options: SpeedTestOptions, *args, **kwargs):
        self.timeout = options.timeout
        self.server_selection_task_name = options.server_selection_task_name
        self.source_ip = options.source_ip
        super().__init__(*args, **kwargs)
    
    def run(self):

        try:
            flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--format=json"]

            if self.server_selection_task_name != '':
                server_id = self.previous_steps.get(self.server_selection_task_name, [Failure(f"{self.server_selection_task_name} not found")])[-1]
                
                if isinstance(server_id, Failure):
                    return server_id
                
                else:
                    flags.append(f"--server-id={server_id}")

            elif self.server_id != '':
                flags.append(f"--ip={self.source_ip}")

            else:
                pass
            
            result = subprocess.run(["speedtest"] + flags, stdout=subprocess.PIPE)
            result.check_returncode()
            return Success({"test_result" : result.stdout})
                
        except subprocess.TimeoutExpired:
            return Failure("Ookla Speedtest timed out.")
        
        except CalledProcessError:
            return Failure(
                    f"Ookla Speedtest failed with return code {result.returncode}. "
                    f"\nStdout: {result.stdout.strip()} "
                    f"\nStderr: {result.stderr.strip()}"
                )
        
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")
        

class ServerSelection(TaskDispatcher):
    """
    Allows users to select a specific server from a list using a callback function.
    """

    def __init__(self, callback: Callable[[list[ServerInfo]], str], *args, **kwargs):
        """
        `callback` will recieve a list of `ServerInfo` and should return a single server id from that list.
        """
        super().__init__(*args, **kwargs)
        self.linux_instance = ServerSelectionLinuxImplementation(callback, name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_instance

        raise NotImplementedError(
            f"ServerSelection is not implemented for architecture: {node.architecture}"
        )

class ServerSelectionLinuxImplementation(Task):
    requirements = UNIX_REQUIREMENTS

    def __init__(self, callback: Callable[[list[ServerInfo]], str], *args, **kwargs):
        self.callback = callback
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--servers", "--format=json"]
            result = subprocess.run(["speedtest"] + flags, stdout=subprocess.PIPE)
            result.check_returncode()
            servers = [
                ServerInfo(
                    server["id"],
                    server["host"],
                    server["port"],
                    server["name"],
                    server["location"],
                    server["country"]
                )
                for server
                in json.loads(result.stdout.decode())["servers"]
            ]
            return self.callback(servers)
        
        except CalledProcessError:
            return Failure(
                f"Ookla_Speedtest_CLI failed with return code {result.returncode}. "
                f"\nStdout: {result.stdout.strip()} "
                f"\nStderr: {result.stderr.strip()}"
            )
        
if __name__ == "__main__":
    cli_task = OoklaSpeedtest(name="Ookla CLI Speedtest")
    print(cli_task.run())

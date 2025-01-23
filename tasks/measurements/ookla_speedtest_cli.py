import subprocess
import json
from typing import Callable

from netunicorn.base import Architecture, Failure, Success, Task, TaskDispatcher, Node
from subprocess import CalledProcessError
from dataclasses import dataclass

@dataclass
class SpeedTestOptions:
    server_id: str = ""
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
        super().__init__(*args, **kwargs)
        self.linux_implementation = OoklaSpeedtestLinuxImplementation(options, name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ookla_Speedtest_CLI is not implemented for architecture: {node.architecture}"
        )
    
class OoklaSpeedtestLinuxImplementation(Task):
    requirements = [
        "apt-get install curl --yes",
        "curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash",
        "apt-get install speedtest --yes",
    ]

    def __init__(self, options: SpeedTestOptions, *args, **kwargs):
        self.timeout = options.timeout
        self.server_id = options.server_id
        # self.source_ip = options.source_ip
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--format=json"]

            if self.server_id != '':
                flags.append(f"--server-id={self.server_id}")
            # if self.source_ip != '':
            #     flags.append(f"--ip={self.source_ip}")
            
            result = subprocess.run(["speedtest"] + flags, stdout=subprocess.PIPE)
            result.check_returncode()
            return Success({"test_result" : result.stdout})
                
        except subprocess.TimeoutExpired:
            return Failure("Ookla Speedtest timed out.")
        
        except CalledProcessError:
            return Failure(
                    f"Ookla_Speedtest_CLI failed with return code {result.returncode}. "
                    f"\nStdout: {result.stdout.strip()} "
                    f"\nStderr: {result.stderr.strip()}"
                )
        
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")
        

class ServerSelection(TaskDispatcher):
    def __init__(self, callback: Callable[[list[ServerInfo]], int], options: SpeedTestOptions = SpeedTestOptions(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_instance = ServerSelectionLinuxImplementation(callback, name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_instance

        raise NotImplementedError(
            f"ServerSelection is not implemented for architecture: {node.architecture}"
        )

class ServerSelectionLinuxImplementation(Task):
    requirements = [
        "apt-get install curl --yes",
        "curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash",
        "apt-get install speedtest --yes",
    ]

    def __init__(self, callback: Callable[[list[ServerInfo]], int], options: SpeedTestOptions, *args, **kwargs):
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
            return {"server_id": self.callback(servers)}
        
        except CalledProcessError:
            return Failure(
                f"Ookla_Speedtest_CLI failed with return code {result.returncode}. "
                f"\nStdout: {result.stdout.strip()} "
                f"\nStderr: {result.stderr.strip()}"
            )
        
if __name__ == "__main__":
    cli_task = OoklaSpeedtest(name="Ookla CLI Speedtest")
    print(cli_task.run())

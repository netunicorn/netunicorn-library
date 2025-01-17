import subprocess
from netunicorn.base.architecture import Architecture # type: ignore
from netunicorn.base.nodes import Node # type: ignore
from netunicorn.base import Failure, Success, Task, TaskDispatcher # type: ignore


class OoklaSpeedtestCLI(TaskDispatcher):
    def __init__(self, target_server: str = '', source_ip: str = '', timeout: int = 120, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_implementation = OoklaSpeedtestCLILinuxImplementation(
            timeout=timeout, target_server=target_server, source_ip=source_ip, name=self.name
        )

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ookla_Speedtest_CLI is not implemented for architecture: {node.architecture}"
        )
    
class OoklaSpeedtestCLILinuxImplementation(Task):
    requirements = ["sudo DEBIAN_FRONTEND=noninteractive apt-get update -y",
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y curl gnupg2",
                    (
                        "curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/"
                        "script.deb.sh | sudo bash"
                    ),
                    "sudo DEBIAN_FRONTEND=noninteractive apt-get install -y speedtest"
                ]
    def __init__(self, target_server: str = '', source_ip: str = '', timeout: int = 120, *args, **kwargs):
        self.timeout = timeout
        self.target_server = target_server
        self.source_ip = source_ip
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--format=json", "-v"]
            if self.target_server != '':
                flags.append(f"--server-id={self.target_server}")
            if self.source_ip != '':
                flags.append(f"--ip={self.source_ip}")
            result = subprocess.run(
                ["speedtest"] + flags,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if result.returncode == 0:
                return Success({"test_result" : result.stdout})
            else:
                return Failure(
                    f"Ookla_Speedtest_CLI failed with return code {result.returncode}. "
                    f"\nStdout: {result.stdout.strip()} "
                    f"\nStderr: {result.stderr.strip()}"
                )
        except subprocess.TimeoutExpired:
            return Failure("Ookla_Speedtest_CLI timed out.")
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    cli_task = OoklaSpeedtestCLI(name="Ookla CLI Speedtest")
    print(cli_task.run())
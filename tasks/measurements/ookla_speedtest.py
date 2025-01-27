import subprocess
import json
from typing import Callable, Optional, List

from netunicorn.base import Architecture, Failure, Success, Task, TaskDispatcher, Node 
from subprocess import CalledProcessError
from dataclasses import dataclass

UNIX_REQUIREMENTS = [
    "apt-get install curl --yes",
    "curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash",
    "apt-get install speedtest --yes",
]

@dataclass
class ServerInfo:
    id: str
    host: str
    port: int
    name: str
    location: str
    country: str

class OoklaSpeedtest(TaskDispatcher):
    def __init__(self, server_selection_task_name: str = "", source_ip: str = "", timeout: int = 100, *args, **kwargs):
        """
        Proivde either `server_selection_task_name` or `source_ip` to ping to a certain server.
        If neither are provided, a server will be automatically selected.
        If both are proived, the server id from the server selection task will be prioritized.
        """
        super().__init__(*args, **kwargs)
        self.linux_implementation = OoklaSpeedtestLinuxImplementation(server_selection_task_name, source_ip, timeout, name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ookla Speedtest is not implemented for architecture: {node.architecture}"
        )
    
class OoklaSpeedtestLinuxImplementation(Task):
    requirements = UNIX_REQUIREMENTS

    def __init__(self,server_selection_task_name: str, source_ip: str, timeout: int, *args, **kwargs):
        self.timeout = timeout
        self.server_selection_task_name = server_selection_task_name
        self.source_ip = source_ip
        super().__init__(*args, **kwargs)
    
    def run(self):

        try:
            flags = ["--accept-gdpr", "--accept-license", "--progress=no", "--format=json"]

            if self.server_selection_task_name != '':
                server_id = self.previous_steps.get(self.server_selection_task_name, [Failure(f"{self.server_selection_task_name} not found")])[-1]
                
                if isinstance(server_id, Failure):
                    return server_id
                
                else:
                    flags.append(f"--server-id={server_id.unwrap()}")

            elif self.source_ip != '':
                flags.append(f"--ip={self.source_ip}")

            else:
                pass
            
            result = subprocess.run(["speedtest"] + flags, stdout=subprocess.PIPE)
            result.check_returncode()
            return Success(json.loads(result.stdout))
                
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
    Inteded to be use in tandem with `OoklaSpeedtest`. Allows users to select a specific server from a list using a callback function.
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

class OoklaSpeedtestAnalysis(TaskDispatcher):
    """
    This task analyzes the results of an Ookla Speedtest by inspecting the latency,
    jitter, and download/upload throughput. It then provides a simple classification
    (e.g. 'good', 'ok', 'strange', 'problem') for latency and throughput results.
    """
    def __init__(self, speedtest_task_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_implementation = OoklaSpeedtestAnalysisLinuxImplementation(
            speedtest_task_name,
            name=self.name
        )
        
    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ookla_Speedtest_CLI is not implemented for architecture: {node.architecture}"
        )

class OoklaSpeedtestAnalysisLinuxImplementation(Task):
    requirements = UNIX_REQUIREMENTS

    def __init__(self, speedtest_task_name: str, *args, **kwargs):
        self.speedtest_task_name = speedtest_task_name
        super().__init__(*args, **kwargs)

    def classify_latency(self, latency_value: float) -> str:
        if latency_value < 10:
            return "good"
        elif latency_value < 30:
            return "ok"
        elif latency_value < 100:
            return "strange"
        else:
            return "problem"

    def classify_throughput(self, bandwidth_bps: float) -> str:
        mbps = bandwidth_bps / 1_000_000
        if mbps < 10:
            return "low"
        elif mbps < 50:
            return "ok"
        elif mbps < 150:
            return "good"
        else:
            return "excellent"

    def run(self):
        try:
            raw_speedtest_results = self.previous_steps.get(self.speedtest_task_name, Failure("Ookla CLI Speedtest Task has not been executed"))

            if isinstance(raw_speedtest_results, Failure):
                return raw_speedtest_results

            speedtest_results = [result.unwrap() for result in raw_speedtest_results]
            ping_latencies: List[float] = []
            ping_jitters: List[float] = []
            download_bandwidths: List[float] = []
            upload_bandwidths: List[float] = []

            for speedtest_data_dict in speedtest_results:
                ping_info = speedtest_data_dict.get("ping", {})
                if "latency" in ping_info:
                    ping_latencies.append(float(ping_info["latency"]))
                if "jitter" in ping_info:
                    ping_jitters.append(float(ping_info["jitter"]))
                download_info = speedtest_data_dict.get("download", {})
                if "bandwidth" in download_info:
                    download_bandwidths.append(float(download_info["bandwidth"]))
                upload_info = speedtest_data_dict.get("upload", {})
                if "bandwidth" in upload_info:
                    upload_bandwidths.append(float(upload_info["bandwidth"]))
 
            def average(values: List[float]) -> float:
                return sum(values) / len(values) if values else 0.0

            avg_latency = average(ping_latencies)
            avg_jitter = average(ping_jitters)
            avg_download_bps = average(download_bandwidths)
            avg_upload_bps = average(upload_bandwidths)

            latency_class = self.classify_latency(avg_latency) if avg_latency > 0 else "Unknown"
            download_class = self.classify_throughput(avg_download_bps) if avg_download_bps > 0 else "Unknown"
            upload_class = self.classify_throughput(avg_upload_bps) if avg_upload_bps > 0 else "Unknown"

            summary = {
                "average_ping_latency_ms": avg_latency,
                "ping_latency_class": latency_class,
                "average_ping_jitter_ms": avg_jitter,
                "average_download_bandwidth_bps": avg_download_bps,
                "download_bandwidth_class": download_class,
                "average_upload_bandwidth_bps": avg_upload_bps,
                "upload_bandwidth_class": upload_class,
            }
            return Success(summary)

        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

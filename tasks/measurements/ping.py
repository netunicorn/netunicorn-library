from dataclasses import dataclass
from typing import List

from netunicorn.base import Architecture, Node, Task, TaskDispatcher
from netunicorn.library.tasks.tasks_utils import subprocess_run


@dataclass
class PacketResult:
    icmp_seq: int
    ttl: int
    time: float
    unit: str


@dataclass
class PingResult:
    host: str
    packets: List[PacketResult]
    packet_loss: float
    min_rtt: float
    avg_rtt: float
    max_rtt: float
    stddev_rtt: float
    unit_rtt: str
    unparsed_output: List[str]
    raw_output: str


class Ping(TaskDispatcher):
    def __init__(self, address: str, count: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address
        self.count = count
        self.linux_implementation = PingLinuxImplementation(self.address, self.count)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation
        raise NotImplementedError(
            f"Ping is not implemented for architecture: {node.architecture}"
        )


class PingLinuxImplementation(Task):
    requirements = ["sudo apt-get install -y iputils-ping"]

    def __init__(self, address: str, count: int = 1, *args, **kwargs):
        self.address = address.strip()
        self.count = count
        super().__init__(*args, **kwargs)

    def run(self):
        return subprocess_run(["ping", self.address, "-c", str(self.count)]).map(
            self._format
        )

    def _format(self, output: str) -> PingResult:
        raw_output = output[:]

        try:
            lines = [x for x in output.split("\n") if x]

            # parse rtt statistics
            rtts, unit = lines[-1].split("=")[1].strip().split(" ")
            rtt_min, rtt_avg, rtt_max, rtt_stddev = [float(x) for x in rtts.split("/")]
            lines = lines[:-1]

            # take packet_loss line and packets received
            _, packets_received, packet_loss, _ = lines[-1].split(",")
            packets_received = int(packets_received.strip().split(" ")[0])
            packet_loss = float(
                packet_loss.removesuffix("packet loss").strip().split("%")[0]
            )
            lines = lines[:-1]

            # remove first and last line
            lines = lines[1:-1]

            # parse received packets
            packets = []
            for packet in lines[:packets_received]:
                packet = packet.split(":")[1]
                seq, ttl, time, unit = [x.strip() for x in packet.split(" ") if x]
                seq = int(seq.split("=")[1])
                ttl = int(ttl.split("=")[1])
                time = float(time.split("=")[1])
                packets.append(PacketResult(seq, ttl, time, unit))
            lines = lines[packets_received:]

            # theoretically, here should be 0 lines left
            unparsed_output = lines

            return PingResult(
                self.address,
                packets,
                packet_loss,
                rtt_min,
                rtt_avg,
                rtt_max,
                rtt_stddev,
                unit,
                unparsed_output,
                raw_output,
            )
        except Exception:
            return PingResult(self.address, [], 100, 0, 0, 0, 0, "", [], raw_output)


if __name__ == "__main__":
    ping = PingLinuxImplementation("8.8.8.8", count=10)
    print(ping.run())

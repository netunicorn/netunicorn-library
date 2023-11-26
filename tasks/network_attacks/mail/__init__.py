from netunicorn.base.task import Task

from .fake_mail import send_mail


class FakeMail(Task):
    def __init__(
        self,
        host: str,
        port: int,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        *args,
        **kwargs
    ):
        self.host = host
        self.port = port
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.body = body
        super().__init__(*args, **kwargs)

    def run(self):
        return send_mail(
            host=self.host,
            port=self.port,
            sender=self.sender,
            recipient=self.recipient,
            subject=self.subject,
            body=self.body,
        )

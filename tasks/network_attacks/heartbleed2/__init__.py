from netunicorn.base.task import Task
from netunicorn.base import Failure, Result, Success
from .heart_bleed   import sendHeartbeat

class Heartbleed(Task):
    def __init__(
        self,
        IPaddress: str,
        port=443,
        starttls=False,
        debug=False,
        *args,
        **kwargs
    ):
        self.IPaddress = IPaddress
        self.port = port
        self.starttls = starttls
        self.debug = debug
        super().__init__(*args, **kwargs)

    def run(self):
        return sendHeartbeat(
            IPaddress = self.IPaddress,
            port = self.port,
            starttls = self.starttls,
            debug = self.debug
        )


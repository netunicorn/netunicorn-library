from netunicorn.base.task import Task
from netunicorn.base import Failure, Result, Success
from .brute_force_ssh import brute_force_ssh

class BruteForceSSH(Task):
    requirements = ["pip install paramiko"]

    def __init__(
        self,
        targetIP: str,
        wordlist: list,
        port=22,
        user="root",
        *args,
        **kwargs
    ):
        self.targetIP = targetIP
        self.wordlist = wordlist
        self.port = port
        self.user = user
        super().__init__(*args, **kwargs)

    def run(self):
        return bruteforce_ssh(
            host = self.targetIP,
            port = self.port,
            username = self.user,
            wordlist = self.wordlist
        )

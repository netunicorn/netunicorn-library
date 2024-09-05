from netunicorn.base.task import Task
from netunicorn.base import Failure, Result, Success
from .brute_force_ftp import brute_force

class BruteForceFTP(Task):
    def __init__(
        self,
        targetIP: str,
        wordlist: list,
        user='root',
        *args,
        **kwargs
    ):
        self.targetIP = targetIP
        self.user = user
        self.wordlist = wordlist
        super().__init__(*args, **kwargs)

    def run(self):
        return brute_force(
            target = self.targetIP,
            username = self.user,
            wordlist = self.wordlist,
        )

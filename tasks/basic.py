import subprocess
import time

from netunicorn.base.task import Task


class DummyTask(Task):
    def run(self):
        return True


class SleepTask(Task):
    def __init__(self, seconds: int, *args, **kwargs):
        self.seconds = seconds
        super().__init__(*args, **kwargs)

    def run(self):
        time.sleep(self.seconds)
        return self.seconds


class ShellCommand(Task):
    def __init__(self, command: str, *args, **kwargs):
        self.command = command
        super().__init__(*args, **kwargs)

    def run(self):
        return subprocess.check_output(self.command, shell=True)

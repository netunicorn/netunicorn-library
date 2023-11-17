import subprocess
import time

from netunicorn.base import Task
from netunicorn.library.tasks.tasks_utils import subprocess_run


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
    def __init__(self, command: list[str], *args, **kwargs):
        self.command = command
        super().__init__(*args, **kwargs)

    def run(self):
        if isinstance(self.command, str):
            # legacy mode
            return subprocess.check_output(self.command, shell=True)
        return subprocess_run(self.command)

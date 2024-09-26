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
        
class SleepUntilTask(Task):
    def __init__(self, target_date_str: str, *args, **kwargs):
        self.target_date_str = target_date_str
        super().__init__(*args, **kwargs)

    def run(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        target_datetime_str = f"{current_date} {target_date_strrr}"
        target_datetime = datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M")

        #Get current time
        current_time = datetime.now()

        # Calculate the number of seconds to sleep
        sleep_seconds = (target_datetime - current_time).total_seconds()

        # Only sleep if the target time is in the future
        if sleep_seconds > 0:
            print(f"Sleeping for {sleep_seconds:.2f} seconds until {target_datetime}")
            time.sleep(sleep_seconds)
            return sleep_seconds
        else:
            print("The target time is in the past. No need to sleep.")
            return 0

class ShellCommand(Task):
    def __init__(self, command: list[str], *args, **kwargs):
        self.command = command
        super().__init__(*args, **kwargs)

    def run(self):
        if isinstance(self.command, str):
            # legacy mode
            return subprocess.check_output(self.command, shell=True)
        return subprocess_run(self.command)

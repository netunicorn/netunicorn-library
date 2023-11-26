import random

from netunicorn.base import Task, TaskDispatcher
from netunicorn.base.nodes import Node
from netunicorn.library.tasks.basic import SleepTask


class RandomSleepTask(TaskDispatcher):
    def __init__(self, seconds_min: int, seconds_max: int, *args, **kwargs):
        self.seconds_min = seconds_min
        self.seconds_max = seconds_max
        super().__init__(*args, **kwargs)

    def dispatch(self, node: Node) -> Task:
        return SleepTask(seconds=random.randint(self.seconds_min, self.seconds_max))

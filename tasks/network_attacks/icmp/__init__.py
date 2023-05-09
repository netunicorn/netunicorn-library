from netunicorn.base.task import Task
from .redirection import main


class ICMPRedirection(Task):
    def __init__(self, target: str, old_gw: str, new_gw: str):
        self.target = target
        self.old_gw = old_gw
        self.new_gw = new_gw
        super().__init__()

    def run(self):
        return main(self.target, self.old_gw, self.new_gw)

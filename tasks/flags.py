from typing import Literal

from netunicorn.base import Task
from netunicorn.base.types import FlagValues


class SetFlagTask(Task):
    def __init__(self, flag_name: str, flag_values: FlagValues, *args, **kwargs):
        if flag_values.int_value is None and flag_values.text_value is None:
            raise ValueError("Either int_value or text_value must be set")

        self.flag_name = flag_name
        self.flag_values = flag_values
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        import requests as req
        import os

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        req.post(
            f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}",
            json=self.flag_values.dict(),
        ).raise_for_status()


class GetFlagTask(Task):
    def __init__(self, flag_name: str, *args, **kwargs):
        self.flag_name = flag_name
        super().__init__(*args, **kwargs)

    def run(self) -> FlagValues:
        import requests as req
        import os

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        result = req.get(
            f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}"
        ).json()
        return FlagValues(**result)


class _AtomicOperationFlagTask(Task):
    def __init__(self, flag_name: str, operation: Literal['increment', 'decrement'], *args, **kwargs):
        self.flag_name = flag_name
        self.operation = operation
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        import requests as req
        import os

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        req.post(
            f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}/{self.operation}",
        ).raise_for_status()


class AtomicIncrementFlagTask(_AtomicOperationFlagTask):
    def __init__(self, flag_name: str, *args, **kwargs):
        super().__init__(flag_name, 'increment', *args, **kwargs)


class AtomicDecrementFlagTask(_AtomicOperationFlagTask):
    def __init__(self, flag_name: str, *args, **kwargs):
        super().__init__(flag_name, 'decrement', *args, **kwargs)

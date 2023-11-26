import warnings
from typing import Literal, Optional
from urllib.parse import quote_plus

from netunicorn.base import Task
from netunicorn.base.types import FlagValues


def quote_plus_and_warn(string: str) -> str:
    result = quote_plus(string)
    if result != string:
        warnings.warn(
            f"String {string} was encoded to {result}. "
            f"Consider using only alphanumeric characters and underscores."
        )

    return result


class SetFlagTask(Task):
    def __init__(self, flag_name: str, flag_values: FlagValues, *args, **kwargs):
        if flag_values.int_value is None and flag_values.text_value is None:
            raise ValueError("Either int_value or text_value must be set")

        self.flag_name = quote_plus_and_warn(flag_name)
        self.flag_values = flag_values
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        import os

        import requests as req

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        req.post(
            f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}",
            json=self.flag_values.dict(),
        ).raise_for_status()


class GetFlagTask(Task):
    def __init__(self, flag_name: str, *args, **kwargs):
        self.flag_name = quote_plus_and_warn(flag_name)
        super().__init__(*args, **kwargs)

    def run(self) -> FlagValues:
        import os

        import requests as req

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        result = req.get(
            f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}"
        )
        result.raise_for_status()
        return FlagValues(**result.json())


class WaitForExactFlagResultTask(Task):
    def __init__(
        self,
        flag_name: str,
        values: FlagValues,
        sleep_time: float = 1,
        attempts: Optional[int] = None,
        *args,
        **kwargs,
    ):
        self.flag_name = quote_plus_and_warn(flag_name)
        self.sleep_time = sleep_time
        self.attempts = attempts
        self.values = values
        super().__init__(*args, **kwargs)

    def run(self) -> FlagValues:
        import os
        import time

        import requests as req

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        result = None
        counter = 0
        while result != self.values:
            request_info = req.get(
                f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}"
            )
            if request_info.status_code == 200:
                result = request_info.json()
                if result and FlagValues(**result) == self.values:
                    break

            # 404 is a normal result -- flag has not been set yet
            if request_info.status_code != 404:
                request_info.raise_for_status()

            counter += 1
            if self.attempts is not None and counter >= self.attempts:
                raise TimeoutError("Timeout while waiting for flag to be set")
            time.sleep(self.sleep_time)

        return result


class _AtomicOperationFlagTask(Task):
    def __init__(
        self,
        flag_name: str,
        operation: Literal["increment", "decrement"],
        *args,
        **kwargs,
    ):
        self.flag_name = quote_plus_and_warn(flag_name)
        self.operation = operation
        super().__init__(*args, **kwargs)

    def run(self) -> None:
        import os

        import requests as req

        gateway = os.environ["NETUNICORN_GATEWAY_ENDPOINT"]
        experiment_id = os.environ["NETUNICORN_EXPERIMENT_ID"]

        req.post(
            f"{gateway}/api/v1/experiment/{experiment_id}/flag/{self.flag_name}/{self.operation}",
        ).raise_for_status()


class AtomicIncrementFlagTask(_AtomicOperationFlagTask):
    def __init__(self, flag_name: str, *args, **kwargs):
        super().__init__(flag_name, "increment", *args, **kwargs)


class AtomicDecrementFlagTask(_AtomicOperationFlagTask):
    def __init__(self, flag_name: str, *args, **kwargs):
        super().__init__(flag_name, "decrement", *args, **kwargs)

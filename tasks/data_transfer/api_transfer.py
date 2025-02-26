import requests
from netunicorn.base import Failure, Success, Task
import uuid

class SendData(Task):
    """
    Sends a netunicorn execution result(s) to an API endpoint
    """
    def __init__(self, tasks_name: list[str], endpoint: str, allow_failure = False, *args, **kwargs):
        self.tasks_name = tasks_name
        self.endpoint = endpoint
        self.allow_failure = allow_failure
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            data = []
            for task_name in self.tasks_name:            
                raw_task_result = self.previous_steps.get(task_name, Failure(f"{task_name} not found"))

                if isinstance(raw_task_result, Failure) and not self.allow_failure:
                    return raw_task_result
                if isinstance(raw_task_result, Failure):
                    continue

                task_results = [result.unwrap() for result in raw_task_result]
                data.append({"id" : str(uuid.uuid1()), "task_name": task_name, "task_results": task_results})

            response = requests.post(self.endpoint, json={"data": data})
            
            if response.status_code == 200:
                return Success(f"Data successfuly transferred to {self.endpoint}.")
            else:
                return Failure(f"Failed to transfer data:\n {response.status_code} {response.text}")
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

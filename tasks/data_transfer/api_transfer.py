import requests
from netunicorn.base import Failure, Success, Task


class SendToAPIEndpoint(Task):
    """
    Sends a netunicorn execution result(s) to any api endpoint
    """
    def __init__(self, task_name: str, api_url: str, *args, **kwargs):
        self.task_name = task_name
        self.url = api_url
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            raw_task_result = self.previous_steps.get(self.task_name, Failure(f"{self.task_name} not found"))
            if isinstance(raw_task_result, Failure):
                return raw_task_result
            task_results = [result.unwrap() for result in raw_task_result]
            data = {"task": self.task_name, "result": task_results}
            response = requests.post(self.url, json=data)
            if response.status_code == 200:
                return Success(f"API endpoint at {self.url} recieved {self.task_name} task results")
            else:
                return Failure(f"Failed to post data: {response.status_code} {response.text}")
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

import requests
from netunicorn.base import Failure, Success, Task
import uuid
from dataclasses import dataclass

class SendData(Task):
    """
    Sends a netunicorn execution result(s) to an API endpoint
    """
    
    @dataclass
    class TaskInfo:
        task_name: str
        task_type: str

    def __init__(
        self, 
        tasks_info: list[TaskInfo], 
        endpoint: str, 
        allow_failure = True, 
        *args, 
        **kwargs
        ):
        
        self.tasks_info = tasks_info
        self.endpoint = endpoint
        self.allow_failure = allow_failure
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            execution_results = []
            for task_info in self.tasks_info:            
                raw_task_result = self.previous_steps.get(task_info.task_name, Failure(f"{task_info.task_name} not found"))

                if isinstance(raw_task_result, Failure) and not self.allow_failure:
                    return raw_task_result
                if isinstance(raw_task_result, Failure):
                    continue

                task_results = [result.unwrap() for result in raw_task_result]
                execution_results.append({"task_type": task_info.task_type, "task_results": task_results})

            response = requests.post(self.endpoint, json={"data": {"execution_id":str(uuid.uuid1()), "execution_results": execution_results}})
            
            if response.status_code == 200:
                return Success(f"Data successfuly transferred to {self.endpoint}.")
            else:
                return Failure(f"Failed to transfer data:\n {response.status_code} {response.text}")
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

import requests
from netunicorn.base import Failure, Success, Task
from dataclasses import dataclass
from typing import Callable, Any, Optional

class SendData(Task):
    """
    Sends a netunicorn speedtest execution result(s) to an API endpoint
    """
    
    @dataclass
    class TaskDescriptor:
        name: str
        handler: Optional[Callable[[list[Any]], Any]] = None
        alias: Optional[str] = None

    def __init__(
        self,
        task_descriptors: list[TaskDescriptor],
        endpoint: str,
        allow_failure = False,
	    payload_handler: Optional[Callable[[dict], Any]] = None,
        *args,
        **kwargs
        ):
        
        self.task_descriptors = task_descriptors
        self.endpoint = endpoint
        self.allow_failure = allow_failure
        self.payload_handler = payload_handler
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            payload = {}
            
            for task_descriptor in self.task_descriptors:            
                raw_task_results = self.previous_steps.get(task_descriptor.name, Failure(f"{task_descriptor.name} not found"))

                if isinstance(raw_task_results, Failure) and not self.allow_failure:
                    return raw_task_results
                
                if isinstance(raw_task_results, Failure):
                    continue

                task_results = [result.unwrap() for result in raw_task_results]
                
                if task_descriptor.handler:
                    task_results = task_descriptor.handler(task_results)
                
                if task_descriptor.alias:
                    payload[task_descriptor.alias] = task_results
                else:
                    payload[task_descriptor.name] = task_results

            if self.payload_handler:
                payload = self.payload_handler(payload)
 
            response = requests.post(self.endpoint, json=payload)

            if response.status_code == 200:
                return Success(response.json())
            else:
                return Failure(f"Failed to transfer data:\n {response.status_code} {response.text}")
            
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

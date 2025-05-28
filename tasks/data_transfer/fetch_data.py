import requests
from netunicorn.base import Failure, Success, Task

class FetchData(Task):
    """
    Recieves speedtest analysis from a RAG
    """
    def __init__(
        self, 
        send_data_task: str,
        endpoint: str,
        *args, 
        **kwargs
        ):
        self.send_data_task = send_data_task
        self.endpoint = endpoint
        super().__init__(*args, **kwargs)
    
    def run(self):
        try:
            send_data_exec = self.previous_steps.get(self.send_data_task, Failure(f"{self.send_data_task} not found"))
            if isinstance(send_data_exec, Failure):
                return send_data_exec
            content_id = None
            for exec in send_data_exec:
                if not isinstance(exec, Failure):
                    content_id = exec.unwrap()["result_id"]
                    break
            if content_id is None:
                return Failure(f"Failed to obtain id from {self.send_data_task}")
            
            response = requests.get(self.endpoint, params = {'result_id' : content_id})
            if response.status_code == 200:
                return Success(f"RAG result: {response.json()}")
            else:
                return Failure(f"Failed to obtain data:\n {response.status_code} {response.text}")
        except Exception as e:
            return Failure(f"Exception occurred: {str(e)}")

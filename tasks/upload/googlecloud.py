"""
Uploads files to Google Cloud Storage with optional OAuth token
"""
from netunicorn.base import Architecture, Node, Task, TaskDispatcher
from netunicorn.library.tasks.tasks_utils import subprocess_run

class UploadToGoogleCloudStorage(TaskDispatcher):
    """
    TaskDispatcher to upload a file to Google Cloud Storage.
    """

    def __init__(self, local_filepath: str, bucket: str, target_filepath: str = "", auth_token: str = None, *args, **kwargs):
        """
        Initializes the UploadToGoogleCloudStorage TaskDispatcher.

        Parameters: 
            local_filepath (str): Path of local file to be uploaded.
            bucket (str): Name of the Google Cloud Storage bucket to upload to.
            target_filepath (str, optional): Path in the bucket where the file will be uploaded. Defaults to root directory ("").
            auth_token (str, optional): Google OAuth token used to authorize upload. Required to upload to a private bucket. Defaults to None.
        """

        super().__init__(*args, **kwargs)
        self.linux_implementation = UploadToGoogleCloudStorageCurlImplementation(
            local_filepath=local_filepath, bucket=bucket, target_filepath=target_filepath, auth_token=auth_token, name=self.name
        )
        self.linux_implementation.requirements = ["sudo apt-get install -y curl"]

    def dispatch(self, node: Node) -> Task:
        """
        Selects the implementation for the UploadToGoogleCloudStorage task based on the detected OS. 
        Currently supports Linux.
        """

        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation

        raise NotImplementedError(
            f"UploadToGoogleCloudStorage is not implemented for architecture: {node.architecture}"
        )


class UploadToGoogleCloudStorageCurlImplementation(Task):
    """
    Task to upload a file to Google Cloud Storage using cURL.

    Requirements: curl package is installed on the node.
    """
    
    def __init__(self, local_filepath: str, bucket: str, target_filepath: str, auth_token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.local_filepath = local_filepath
        self.bucket = bucket
        self.target_filepath = target_filepath
        self.auth_token = auth_token

    def run(self):
        """
        Uploads the local file to the target Google Cloud Storage bucket. 

        Returns: 
            Success or Failure, depending on if an error occurred. 
        """

        command = [
            "curl",
            "--fail",
            "-v",
            "--upload-file",
            f"{self.local_filepath}",
        ]
        if self.auth_token is not None:
            command += ["-H", f"Authorization: Bearer {self.auth_token}"]
        command.append(f"https://storage.googleapis.com/{self.bucket}/{self.target_filepath}")
        return subprocess_run(command)
import os
from ftplib import FTP, error_perm

from netunicorn.base import Failure, Result, Success, Task


class UploadToFTP(Task):
    """
    Task for uploading a local file to an FTP Server. Establishes a connection to the specified FTP server, navigates to the desired remote directory, and uploads the specified local file.
    """

    def __init__(
        self,
        local_filepath: str,
        ftp_url: str,
        username: str,
        password: str,
        destination_dir: str = "/",
        timeout: int = 30,
        *args,
        **kwargs,
    ):
        """
        Initializes the UploadToFTP task with parameters.

        Parameters:
          local_filepath (str): Path to local file to upload.
          ftp_url (str): URL or IP address of FTP.
          username (str): Username credential for FTP auth.
          password (str): Password credential for FTP auth.
          destination_dir (str): Destination directory on the FTP server where the file will be uploaded to. Defaults to "/".
          timeout (int, optional): Timeout value for FTP connection measued in seconds. Defaults to 30 seconds.
        """
        super().__init__(*args, **kwargs)
        self.local_filepath = local_filepath
        self.ftp_url = ftp_url
        self.username = username
        self.password = password
        self.destination_dir = destination_dir
        self.timeout = timeout

    def run(self) -> Result:
        """
        Uploads the local file to FTP server.

        Steps:
        1. Finds the specified local file.
        2. Connects to FTP server using provided credentials.
        3. Sets remote directory if specified, else defaults to "/".
        4. Uploads the local file to FTP server and closes connection.

        Returns:
          Result:
            Success: Contains a success message if successful upload.
            --OR--
            Failure: Contains an error message if upload fails.

        """
        try:
            if not os.path.isfile(self.local_filepath):
                return Failure(f"Local file does not exist: {self.local_filepath}")

            ftp = FTP(self.ftp_url, timeout=self.timeout)  # Modify timeout as needed
            ftp.login(user=self.username, passwd=self.password)

            if self.destination_dir:
                ftp.cwd(self.destination_dir)

            with open(self.local_filepath, "rb") as f:
                remote_filename = os.path.basename(self.local_filepath)
                ftp.storbinary(f"STOR {remote_filename}", f)

            ftp.quit()
            return Success(
                f"Successfully uploaded {self.local_filepath} to {self.ftp_url}/{self.destination_dir}"
            )

        except FileNotFoundError:
            return Failure(f"File not found: {self.local_filepath}")

        except error_perm as e:
            return Failure(f"FTP permission error: {e}")

        except Exception as e:
            return Failure(f"An unexpected error occurred: {str(e)}")


class RetrieveFromFTP(Task):
    """
    Task for retrieving a file from an FTP server to a local directory. Establishes a connection to the specified FTP server, navigates to the desired remote directory and downloads the specified file to a local directory.
    """

    def __init__(
        self,
        ftp_remote_filepath: str,
        ftp_url: str,
        username: str,
        password: str,
        local_dir: str = "./",
        timeout: int = 30,
        *args,
        **kwargs,
    ):
        """
        Initializes the RetrieveFromFTP task with parameters.

        Parameters:
          ftp_remote_filepath (str): Full path of the file on the FTP server to retrieve.
          ftp_url (str): URL or IP address of the FTP server.
          username (str): Username for FTP authentication.
          password (str): Password for FTP authentication.
          local_dir (str, optional): Local directory to save the retrieved file. Defaults to "./".
          timeout (int, optional): Timeout value for FTP connection measued in seconds. Defaults to 30 seconds.
          *args: Variable length argument list.
          **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.ftp_remote_filepath = ftp_remote_filepath
        self.ftp_url = ftp_url
        self.username = username
        self.password = password
        self.local_dir = local_dir
        self.timeout = timeout

    def run(self) -> Result:
        """
        Run the FTP file retrieval process.

        Steps:
        1. Connects to FTP server using provided credentials.
        2. Navigates to the directory containing the target file.
        3. Downloads the specified file to the local directory. Defaults to "./".

        Returns:
          Result:
            Success: Contain success message upon successful download.
            --OR--
            Failure: Contains an error message if the download fails.

        """
        try:
            if not os.path.isdir(self.local_dir):
                os.makedirs(self.local_dir, exist_ok=True)

            ftp = FTP(self.ftp_url, timeout=self.timeout)  # Modify timeout as needed
            ftp.login(user=self.username, passwd=self.password)

            remote_dir, remote_filename = os.path.split(self.ftp_remote_filepath)
            if remote_dir:
                ftp.cwd(remote_dir)

            local_filepath = os.path.join(self.local_dir, remote_filename)
            with open(local_filepath, "wb") as f:
                ftp.retrbinary(f"RETR {remote_filename}", f.write)

            ftp.quit()

            return Success(
                f"Successfully downloaded {self.ftp_remote_filepath} to {local_filepath}"
            )

        except FileNotFoundError:
            return Failure(f"File not found: {self.ftp_remote_filepath}")

        except error_perm as e:
            return Failure(f"FTP permission error: {e}")

        except Exception as e:
            return Failure(f"An unexpected error occurred: {str(e)}")

import os
from ftplib import FTP, error_perm

from netunicorn.base import Failure, Result, Success, Task


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
          *args: Variable length argument list.
          **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.ftp_remote_filepath = ftp_remote_filepath
        self.ftp_url = ftp_url
        self.username = username
        self.password = password
        self.local_dir = local_dir

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
            ftp = FTP(self.ftp_url, timeout=30)  # Modify timeout as needed
            ftp.login(user=self.username, passwd=self.password)

            remote_dir, remote_filename = os.path.split(self.ftp_remote_filepath)
            if remote_dir:
                ftp.cwd(remote_dir)

            if not os.path.isdir(self.local_dir):
                return Failure(f"Local directory does not exist: {self.local_dir}")

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

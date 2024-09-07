# Use the provided docker files (ARM or AMD based on your system) to build the docker image

import os
import random
import subprocess
import time
from typing import Optional
from netunicorn.client.remote import RemoteClient, RemoteClientException
from netunicorn.base import Experiment, ExperimentStatus, Pipeline
from netunicorn.library.tasks.capture.tcpdump import StartCapture, StopNamedCapture
from netunicorn.library.tasks.upload.fileio import UploadToFileIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def watch(
    url: str, username: str, password:str, duration: Optional[int] = 100, chrome_location: Optional[str] = None, webdriver_arguments: Optional[list] = None
) -> Result[str, str]:
    
    display_number = random.randint(100, 500)
    xvfb_process = subprocess.Popen(
        ["Xvfb", f":{display_number}", "-screen", "0", "1920x1080x24"]
    )
    os.environ["DISPLAY"] = f":{display_number}"
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    driver = webdriver.Chrome(service=Service(), options=options)
    time.sleep(1)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # Find and fill the username
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_field.send_keys(username)

    # Find and fill the password
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)

    # Find and check the checkbox
    checkbox_label = driver.find_element(By.CSS_SELECTOR, "label[for='location']")
    checkbox_label.click()

    # Find and click the login button
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    
    # Optionally, wait and check if login was successful
    time.sleep(5)  # Wait for a    

    if duration:
        time.sleep(duration)
        result = Success(f"Video finished by timeout: {duration} seconds")
    else:
        result = Success("Video finished by reaching the end")

    driver.close()
    xvfb_process.kill()
    return result



class WatchPufferVideo(TaskDispatcher):
    def __init__(
            self,
            video_url: str,
            username: str,
            password: str,
            duration: Optional[int] = None,
            chrome_location: Optional[str] = None,
            webdriver_arguments: Optional[list] = None,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.video_url = video_url
        self.username = username
        self.password = password
        self.duration = duration
        self.chrome_location = chrome_location
        self.webdriver_arguments = webdriver_arguments
        self.linux_implementation = WatchVimeoVideoLinuxImplementation(
            self.video_url,
            self.username,
            self.password,
            self.duration,
            self.chrome_location,
            self.webdriver_arguments,
            name=self.name
        )

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation

        raise NotImplementedError(
            f'WatchPufferVideo is not implemented for architecture: {node.architecture}'
        )


class WatchPufferVideoLinuxImplementation(Task):
    requirements = [
        "apt install -y python3-pip wget xvfb procps chromium chromium-driver",
        "pip3 install selenium webdriver-manager",
    ]

    def __init__(
        self,
        video_url: str,
        username: str,
        password: str,
        duration: Optional[int] = None,
        chrome_location: Optional[str] = None,
        webdriver_arguments: Optional[list] = None,
        *args,
        **kwargs
    ):
        self.video_url = video_url
        self.username = username
        self.password = password
        self.duration = duration
        self.chrome_location = chrome_location
        if not self.chrome_location:
            self.chrome_location = "/usr/bin/chromium"
        self.webdriver_arguments = webdriver_arguments
        super().__init__(*args, **kwargs)

    def run(self):
        return watch(self.video_url, self.username, self.password ,self.duration, self.chrome_location, self.webdriver_arguments)




if __name__ == "__main__":
    # use the user name and password you have for puffer website
    print(watch("http:128.111.5.228:8080/player/", "jaber" , "jaber-password",30))

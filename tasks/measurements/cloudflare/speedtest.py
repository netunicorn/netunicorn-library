import os
import random
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

from netunicorn.base import Architecture, Node, Result, Success, Task, TaskDispatcher


@dataclass
class CloudflareSpeedTestResults:
    summary: dict
    unloaded_latency: float
    unloaded_jitter: float
    unloaded_latency_points: list[float]
    down_loaded_latency: float
    down_loaded_jitter: float
    down_loaded_latency_points: list[float]
    up_loaded_latency: float
    up_loaded_jitter: float
    up_loaded_latency_points: list[float]
    download_bandwidth: float
    download_bandwidth_points: list[dict]
    upload_bandwidth: float
    upload_bandwidth_points: list[dict]
    packet_loss: float
    packet_loss_details: dict
    scores: dict


def get_measurements(driver) -> CloudflareSpeedTestResults:
    return CloudflareSpeedTestResults(
        summary=driver.execute_script(
            "return window.testInstance.results.getSummary()"
        ),
        unloaded_latency=driver.execute_script(
            "return window.testInstance.results.getUnloadedLatency()"
        ),
        unloaded_jitter=driver.execute_script(
            "return window.testInstance.results.getUnloadedJitter()"
        ),
        unloaded_latency_points=driver.execute_script(
            "return window.testInstance.results.getUnloadedLatencyPoints()"
        ),
        down_loaded_latency=driver.execute_script(
            "return window.testInstance.results.getDownLoadedLatency()"
        ),
        down_loaded_jitter=driver.execute_script(
            "return window.testInstance.results.getDownLoadedJitter()"
        ),
        down_loaded_latency_points=driver.execute_script(
            "return window.testInstance.results.getDownLoadedLatencyPoints()"
        ),
        up_loaded_latency=driver.execute_script(
            "return window.testInstance.results.getUpLoadedLatency()"
        ),
        up_loaded_jitter=driver.execute_script(
            "return window.testInstance.results.getUpLoadedJitter()"
        ),
        up_loaded_latency_points=driver.execute_script(
            "return window.testInstance.results.getUpLoadedLatencyPoints()"
        ),
        download_bandwidth=driver.execute_script(
            "return window.testInstance.results.getDownloadBandwidth()"
        ),
        download_bandwidth_points=driver.execute_script(
            "return window.testInstance.results.getDownloadBandwidthPoints()"
        ),
        upload_bandwidth=driver.execute_script(
            "return window.testInstance.results.getUploadBandwidth()"
        ),
        upload_bandwidth_points=driver.execute_script(
            "return window.testInstance.results.getUploadBandwidthPoints()"
        ),
        packet_loss=driver.execute_script(
            "return window.testInstance.results.getPacketLoss()"
        ),
        packet_loss_details=driver.execute_script(
            "return window.testInstance.results.getPacketLossDetails()"
        ),
        scores=driver.execute_script("return window.testInstance.results.getScores()"),
    )


def measure(
    chrome_location: Optional[str] = None, webdriver_arguments: Optional[list] = None
) -> CloudflareSpeedTestResults:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    # start python http.server
    http_process = subprocess.Popen(
        ["python3", "-m", "http.server", "44345"], cwd="/tmp/cloudflare/speedtest"
    )

    # start Xvfb display for the browser
    display_number = random.randint(100, 500)
    xvfb_process = subprocess.Popen(
        ["Xvfb", f":{display_number}", "-screen", "0", "1920x1080x24"]
    )
    os.environ["DISPLAY"] = f":{display_number}"

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if webdriver_arguments:
        for argument in webdriver_arguments:
            options.add_argument(argument)
    if chrome_location:
        options.binary_location = chrome_location

    driver = webdriver.Chrome(service=Service(), options=options)
    time.sleep(1)
    driver.get("http://localhost:44345/test.html")
    time.sleep(1)

    # check "window.testInstance.isFinished" attribute
    while not driver.execute_script("return window.testInstance.isFinished"):
        time.sleep(1)

    # get results
    results = get_measurements(driver)

    driver.close()
    xvfb_process.kill()
    http_process.kill()
    return results


class CloudflareSpeedTest(TaskDispatcher):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.linux_instance = CloudflareSpeedTestLinuxImplementation(name=self.name)

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_instance

        raise NotImplementedError(
            f"CLoudflareSpeedTest is not implemented for architecture: {node.architecture}"
        )


class CloudflareSpeedTestLinuxImplementation(Task):
    requirements = [
        "apt install -y python3-pip wget xvfb procps chromium chromium-driver",
        "pip3 install selenium webdriver-manager",
        "mkdir -p /tmp/cloudflare/speedtest",
        "wget https://github.com/netunicorn/netunicorn-library/releases/download/cloudflare-speedtest-0.1/bundle.js -O /tmp/cloudflare/speedtest/bundle.js",
        "wget https://github.com/netunicorn/netunicorn-library/releases/download/cloudflare-speedtest-0.1/test.html -O /tmp/cloudflare/speedtest/test.html",
    ]

    def __init__(
        self,
        chrome_location: Optional[str] = None,
        webdriver_arguments: Optional[list] = None,
        *args,
        **kwargs,
    ):
        self.chrome_location = chrome_location
        if not self.chrome_location:
            self.chrome_location = "/usr/bin/chromium"
        self.webdriver_arguments = webdriver_arguments
        super().__init__(*args, **kwargs)

    def run(self) -> Result[CloudflareSpeedTestResults, str]:
        return Success(measure(self.chrome_location, self.webdriver_arguments))


if __name__ == "__main__":
    CloudflareSpeedTestLinuxImplementation(
        chrome_location="/usr/bin/chromium-browser"
    ).run()

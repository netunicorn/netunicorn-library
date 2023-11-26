import os
import subprocess
import time
from typing import Optional

from jinja2 import Environment, FileSystemLoader
from netunicorn.base import Failure, Success, Task, TaskDispatcher, is_successful
from netunicorn.base.architecture import Architecture
from netunicorn.base.nodes import Node


class StartQoECollectionServer(TaskDispatcher):
    def __init__(
        self, data_folder: str = ".", interface: str = "0.0.0.0", port: int = 34543, *args, **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.data_folder = data_folder
        self.interface = interface
        self.port = port
        self.linux_implementation = StartQoECollectionServerLinuxImplementation(
                self.data_folder, self.interface, self.port, name=self.name
            )

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation

        raise NotImplementedError(
            f'StartQoECollectionServer is not implemented for {node.architecture}'
        )


class StartQoECollectionServerLinuxImplementation(Task):
    requirements = [
        "sudo apt-get update",
        "sudo apt-get install -y python3-pip uvicorn",
        "pip3 install fastapi uvicorn uvloop",
    ]

    def __init__(
        self, data_folder: str = ".", interface: str = "0.0.0.0", port: int = 34543, *args, **kwargs,
    ):
        self.data_folder = data_folder
        self.interface = interface
        self.port = port
        super().__init__(*args, **kwargs)

    def run(self):
        env = os.environ.copy()
        env["QOE_DATA_FOLDER"] = self.data_folder

        process = subprocess.Popen(
            [
                "uvicorn",
                "netunicorn.library.tasks.qoe_youtube.qoe_collector:app",
                "--host",
                self.interface,
                "--port",
                str(self.port),
                "--log-level",
                "warning",
            ],
            env=env,
        )
        time.sleep(3)

        if (exitcode := process.poll()) is not None:
            return Failure(
                f"QoE collection server failed to start: exitcode={exitcode}"
            )

        return (
            f"QoE collection server started with data folder '{self.data_folder}' and "
            f"using interface {self.interface}:{self.port}, process ID: {process.pid}",
            process.pid,
        )


class StopQoECollectionServer(TaskDispatcher):
    def __init__(self, start_task_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_task_name = start_task_name
        self.linux_implementation = StopQoECollectionServerLinuxImplementation(
            start_task_name=self.start_task_name, name=self.name
        )

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation

        raise NotImplementedError(
            f'StopQoECollectionServer is not implemented for {node.architecture}'
        )


class StopQoECollectionServerLinuxImplementation(Task):
    def __init__(self, start_task_name: str, *args, **kwargs):
        self.start_task_name = start_task_name
        super().__init__(*args, **kwargs)

    def run(self):
        # look for the process ID of the QoE collection server and use it to kill the server
        result = self.previous_steps.get(self.start_task_name, [Failure("QoE collection server not found")])[-1]
        if is_successful(result):
            process_id = result.unwrap()[1]
            return subprocess.check_output(f"kill {process_id}", shell=True)

        return result


class WatchYouTubeVideo(TaskDispatcher):
    def __init__(
        self,
        video_url: str,
        duration: Optional[int] = None,
        quality: Optional[int] = None,
        qoe_server_address: str = "localhost",
        qoe_server_port: int = 34543,
        report_time: int = 250,
        *args,
        **kwargs,
    ):
        self.video_url = video_url
        self.duration = duration
        self.quality = quality
        self.qoe_server_address = qoe_server_address
        self.qoe_server_port = qoe_server_port
        self.report_time = report_time
        super().__init__(*args, **kwargs)
        self.linux_implementation = WatchYouTubeVideoLinuxImplementation(
                self.video_url,
                self.duration,
                self.quality,
                self.qoe_server_address,
                self.qoe_server_port,
                self.report_time,
                name=self.name,
            )

    def dispatch(self, node: Node) -> Task:
        if node.architecture in {Architecture.LINUX_AMD64, Architecture.LINUX_ARM64}:
            return self.linux_implementation

        raise NotImplementedError(
            f'WatchYouTubeVideo is not implemented for architecture: {node.architecture}'
        )


class WatchYouTubeVideoLinuxImplementation(Task):
    requirements = [
        "sudo apt update",
        "sudo apt install -y python3-pip wget xvfb unzip",
        "pip3 install selenium webdriver-manager Jinja2==3.0.1",
        "wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
        "sudo apt install -y ./google-chrome-stable_current_amd64.deb",
        "sudo apt install -y -f",
        'python3 -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager(path="/usr/bin/").install()"',
        "wget https://github.com/nectostr/pinot_minion_tasks/raw/collection/QoE_youtube/extensions/4.46.2_0.crx -P ./extensions",
        "wget https://github.com/nectostr/pinot_minion_tasks/releases/download/public/qoe_extension.zip -P ./extensions",
        "unzip ./extensions/qoe_extension.zip -d ./extensions/qoe_extension",
    ]

    def __init__(
        self,
        video_url: str,
        duration: Optional[int] = None,
        quality: Optional[int] = None,
        qoe_server_address: str = "localhost",
        qoe_server_port: int = 34543,
        report_time: int = 250,
        *args,
        **kwargs,
    ):
        self.video_url = video_url
        self.duration = duration
        self.quality = quality
        self.qoe_server_address = qoe_server_address
        self.qoe_server_port = qoe_server_port
        self.report_time = report_time
        super().__init__(*args, **kwargs)

    def run(self):
        from netunicorn.library.tasks.qoe_youtube import watcher

        adblock_crx_path = os.path.join(".", "extensions", "4.46.2_0.crx")
        qoe_extension_path = os.path.join(".", "extensions", "qoe_extension")

        # using jinja substitute QoECollectionServer address and port in script.json
        env = Environment(loader=FileSystemLoader(qoe_extension_path))
        template = env.get_template("script.js.template")
        output = template.render(
            server_address=self.qoe_server_address,
            server_port=self.qoe_server_port,
            report_time=self.report_time,
        )
        with open(os.path.join(qoe_extension_path, "script.js"), "w") as f:
            f.write(output)

        # set STATSFORNERDS_PATH and ADBLOCK_PATH variables
        watcher.STATSFORNERDS_PATH = qoe_extension_path
        watcher.ADBLOCK_PATH = adblock_crx_path

        # run watcher
        return watcher.watch(self.video_url, self.duration, self.quality)

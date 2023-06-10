from netunicorn.base import Pipeline
from netunicorn.library.tasks.capture.tcpdump import StartCapture, StopNamedCapture
from netunicorn.library.tasks.measurements.ookla_speedtest import SpeedTest
from netunicorn.library.tasks.upload.fileio import UploadToFileIO


def simple_speedtest_pipeline() -> Pipeline:
    """
    Run a speedtest while capturing the traffic with tcpdump and upload the capture file to file.io
    :return: pipeline to run
    """
    pipeline = (
        Pipeline()
        .then(StartCapture(filepath="/tmp/capture.pcap", name="capture"))
        .then(SpeedTest())
        .then(StopNamedCapture(start_capture_task_name="capture"))
        .then(UploadToFileIO(filepath="/tmp/capture.pcap", expires="1d"))
    )
    return pipeline

from netunicorn.base import Pipeline
from netunicorn.library.tasks.measurements.ookla_speedtest import OoklaSpeedtest
from netunicorn.library.tasks.measurements.ndt import NDT7SpeedTest
from netunicorn.library.tasks.data_transfer.send_data import SendData
from netunicorn.library.tasks.data_transfer.fetch_data import FetchData
from netunicorn.library.tasks.handlers.ookla import ookla_handler
from netunicorn.library.tasks.handlers.mlab import mlab_handler
import os 

def netflex_ookla_full_loop_pipeline() -> Pipeline:
    """
    Run a speedtest using ookla CLI and then providing user-friendly analysis of the results
    through passing the results to a RAG.
    :return: pipeline to run
    """
    pipeline = (
        Pipeline()
        .then(OoklaSpeedtest(name="Ookla CLI Speedtest"))
        .then(SendData(task_descriptors=[SendData.TaskDescriptor("Ookla CLI Speedtest", "ookla-speedtest", ookla_handler)], endpoint=os.getenv('RAG_ENDPOINT'), name="send"))
        .then(FetchData(send_data_task="send", endpoint=os.getenv("RAG_ENDPOINT"), name="fetch"))
    )
    return pipeline

def netflex_mlab_full_loop_pipeline() -> Pipeline:
    """
    Run a speedtest using mlab CLI and then providing user-friendly analysis of the results
    through passing the results to a RAG.
    :return: pipeline to run
    """
    pipeline = (
        Pipeline()
        .then(NDT7SpeedTest(name="test", flags=["-format", "json"]))
        .then(SendData(task_descriptors=[SendData.TaskDescriptor("test", "mlab-speedtest", mlab_handler)], endpoint=os.getenv('RAG_ENDPOINT'), name="send"))
        .then(FetchData(send_data_task="send", endpoint=os.getenv("RAG_ENDPOINT"), name="fetch"))
    )
    return pipeline

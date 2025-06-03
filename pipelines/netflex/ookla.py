import os
from netunicorn.base import Pipeline
from netunicorn.library.tasks.measurements.ookla_speedtest import OoklaSpeedtest
from netunicorn.library.tasks.data_transfer.send_data import SendData
from netunicorn.library.tasks.data_transfer.fetch_data import FetchData
from .utils.ookla import ookla_data_handler

def netflex_ookla_full_loop_pipeline() -> Pipeline:
    """
    Run a speedtest using ookla CLI and then providing user-friendly analysis of the results
    through passing the results to a RAG.
    :return: pipeline to run
    """
    pipeline = (
        Pipeline()
        .then(OoklaSpeedtest(name="ookla-speedtest"))
        .then(SendData(
            task_descriptors=[SendData.TaskDescriptor(
                name="ookla-speedtest",
                handler=ookla_data_handler,
                alias="speedtest"
            )],
            payload_handler=netflex_payload_transformer
            endpoint=os.getenv('RAG_ENDPOINT'),
            name="send"
        ))
        .then(FetchData(send_data_task="send", endpoint=os.getenv("RAG_ENDPOINT"), name="fetch"))
    )
    return pipeline
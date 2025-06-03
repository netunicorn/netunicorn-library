import os
from netunicorn.base import Pipeline
from netunicorn.library.tasks.measurements.ndt import NDT7SpeedTest
from netunicorn.library.tasks.data_transfer.send_data import SendData
from netunicorn.library.tasks.data_transfer.fetch_data import FetchData
from .utils.mlab import mlab_data_handler

def netflex_mlab_full_loop_pipeline() -> Pipeline:
    """
    Run a speedtest using mlab CLI and then providing user-friendly analysis of the results
    through passing the results to a RAG.
    :return: pipeline to run
    """
    pipeline = (
        Pipeline()
        .then(NDT7SpeedTest(name="NDT7-speedtest", flags=["-format", "json"]))
        .then(SendData(
            task_descriptors=[SendData.TaskDescriptor(
                name="NDT7-speedtest",
                handler=mlab_data_handler,
                alias="speedtest"
            )],
            endpoint=os.getenv('RAG_ENDPOINT'),
            name="send"
        ))
        .then(FetchData(send_data_task="send", endpoint=os.getenv("RAG_ENDPOINT"), name="fetch"))
    )
    return pipeline
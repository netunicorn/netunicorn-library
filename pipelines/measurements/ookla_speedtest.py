from netunicorn.base import Pipeline
from netunicorn.library.tasks.measurements.ookla_speedtest import OoklaSpeedtest, OoklaSpeedtestAnalysis

def simple_speedtest_pipeline() -> Pipeline:
    """
    Run a speedtest using ookla CLI and then providing user-friendly analysis of the results
    :return: pipeline to run
    """
    pipeline = (
        Pipeline()
        .then(OoklaSpeedtest(name="Ookla CLI Speedtest"))
        .then(OoklaSpeedtestAnalysis(name="Ookla Speedtest Analysis", speedtest_task_name="Ookla CLI Speedtest"))
    )
    return pipeline

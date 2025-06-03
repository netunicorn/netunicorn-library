def mlab_data_handler(results: list[dict]) -> dict:
    return {
        "task_type": "mlab-speedtest",
        "task_results": {
            "data": results
        }
    }
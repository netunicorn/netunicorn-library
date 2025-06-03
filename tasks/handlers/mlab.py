def mlab_handler(task_type: str, results: list[dict]) -> dict:
    return {
        "task_type": task_type,
        "task_results": {
            "data": results
        }
    }

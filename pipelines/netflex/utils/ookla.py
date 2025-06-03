def ookla_data_handler(results: list[dict]) -> dict:
    for result in results:
        result.pop("interface", None)
        
    return {
        "task_type": "ookla-speedtest", 
        "task_results": results
    }

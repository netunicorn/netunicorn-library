def ookla_handler(task_type: str, results: list[dict]) -> dict:
    for r in results:
        r.pop("interface", None) 
    return {"task_type": task_type, "task_results": results}

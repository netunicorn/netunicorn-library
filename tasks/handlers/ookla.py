def ookla_handler(results: list[dict]) -> dict:
    for r in results:
        r.pop("interface")
    return {"task_results": results}

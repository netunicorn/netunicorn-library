import requests
from returns.result import Failure, Result, Success


def validate_http_01(domain: str, token_name: str, token_data: str) -> Result[None, str]:
    url = f"http://{domain}/.well-known/acme-challenge/{token_name}"
    try:
        response = requests.get(url)
        if response.status_code != 200 or response.content.decode("utf-8") != token_data:
            return Failure(f"HTTP status code {response.status_code}")
        return Success(None)
    except Exception as e:
        return Failure(str(e))


def validate_dns_01(domain: str, token: str) -> Result[None, str]:
    import dns.resolver
    try:
        result = dns.resolver.resolve(f"_acme-challenge.{domain}", "TXT")
        result = list(result.response.answer[0])[-1].strings[0]
        if result.decode("utf-8") != token:
            return Failure(f"DNS validation failed")
        return Success(None)
    except Exception as e:
        return Failure(str(e))

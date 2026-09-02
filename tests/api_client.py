from collections.abc import Mapping

import requests


class ApiClient:
    def __init__(self, base_url: str, auth: tuple[str, str] | None, timeout: float):
        self.base_url = f"{base_url}/api/v1"
        self.auth = auth
        self.timeout = timeout

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        return requests.request(
            method,
            f"{self.base_url}/{path.lstrip('/')}",
            auth=self.auth,
            timeout=self.timeout,
            **kwargs,
        )

    def get(
        self, path: str, params: Mapping | None = None, **kwargs
    ) -> requests.Response:
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Mapping | None = None, **kwargs) -> requests.Response:
        return self.request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: Mapping | None = None, **kwargs) -> requests.Response:
        return self.request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: Mapping | None = None, **kwargs) -> requests.Response:
        return self.request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

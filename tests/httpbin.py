from urllib.parse import urljoin

import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class Httpbin(DockerContainer):
    """
    An HTTP request & response service

    https://httpbin.org/
    """

    IMAGE_NAME = "kennethreitz/httpbin"
    PUBLISHED_PORT = 80

    def __init__(self, **kwargs):
        super().__init__(self.IMAGE_NAME, **kwargs)
        self.with_exposed_ports(self.PUBLISHED_PORT)

    def start(self):
        super().start()
        self.is_ready()
        return self

    @wait_container_is_ready()
    def is_ready(self) -> bool:
        try:
            requests.get(self.get_base_url())
            return True
        except Exception:
            raise

    def get_base_url(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(self.PUBLISHED_PORT)}"

    def get_url(self, path: str) -> str:
        return urljoin(self.get_base_url(), path)

import json
from datetime import datetime

import requests


# TODO make it a namedtuple
class UrlProbe:
    def __init__(self, url, timestamp, http_status_code, response_time_ms):
        self.response_time_ms = response_time_ms
        self.http_status_code = http_status_code
        self.timestamp = timestamp
        self.url = url

    def __str__(self) -> str:
        return json.dumps({
            "url": self.url,
            "timestamp": self.timestamp,
            "http_status_code": self.http_status_code,
            "response_time_ms": self.response_time_ms
        })

    @staticmethod
    def from_json(data):
        url_probe_result = json.loads(data)
        return UrlProbe(
            url=url_probe_result["url"],
            timestamp=url_probe_result["timestamp"],
            http_status_code=url_probe_result["http_status_code"],
            response_time_ms=url_probe_result["response_time_ms"],
        )


def probe_url(url):
    now = datetime.utcnow()
    response = requests.get(url, timeout=5000)
    return UrlProbe(
        url=url,
        timestamp=str(now),
        http_status_code=response.status_code,
        response_time_ms=int(response.elapsed.microseconds / 1000)
    )

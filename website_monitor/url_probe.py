import json
from collections import namedtuple
from datetime import datetime

import requests


class UrlProbe(
    namedtuple("UrlProbe", ["url", "timestamp", "http_status_code", "response_time_ms"])
):
    @classmethod
    def probe(cls, url):
        now = datetime.utcnow()
        response = requests.get(url, timeout=5000)
        return cls(
            url=url,
            timestamp=now,
            http_status_code=response.status_code,
            response_time_ms=int(response.elapsed.total_seconds() * 1000),
        )

    @property
    def json(self):
        def serialize(obj):
            if type(obj) == datetime:
                return str(obj)
            return obj

        return json.dumps(self._asdict(), default=serialize)

    @classmethod
    def from_json(cls, data):
        def deserialize(dct):
            dct.update(timestamp=datetime.fromisoformat(dct["timestamp"]))
            return dct

        return cls(**(json.loads(data, object_hook=deserialize)))

import json
from datetime import datetime

import pytest

from tests.httpbin import Httpbin
from website_monitor.url_probe import UrlProbe


class TestUrlProbe:
    @pytest.mark.parametrize("path", ["/status/200", "/status/400"])
    def test_has_url(self, httpbin: Httpbin, path: str):
        url = httpbin.get_url(path)
        result = UrlProbe.probe(url)
        assert result.url == url

    def test_records_utc_now_as_timestamp(self, httpbin: Httpbin):
        before = datetime.utcnow()
        url = httpbin.get_url(f"/status/200")
        result = UrlProbe.probe(url)
        after = datetime.utcnow()

        assert before < result.timestamp < after

    @pytest.mark.parametrize("http_status_code", [200, 400])
    def test_has_status_code(self, httpbin: Httpbin, http_status_code: int):
        url = httpbin.get_url(f"/status/{http_status_code}")
        result = UrlProbe.probe(url)
        assert result.http_status_code == http_status_code

    @pytest.mark.parametrize("delay_s", [0.1, 2])
    def test_measures_response_time(self, httpbin: Httpbin, delay_s: float):
        url = httpbin.get_url(f"/delay/{delay_s}")
        result = UrlProbe.probe(url)

        margin_ms = 20
        at_least = (delay_s * 1000) - margin_ms
        at_most = (delay_s * 1000) + margin_ms

        assert at_least < result.response_time_ms < at_most

    def test_serializes_to_json(self):
        assert json.loads(
            UrlProbe(
                url="https://json.test",
                timestamp=datetime.min,
                http_status_code=123,
                response_time_ms=456,
            ).json
        ) == json.loads(
            """{
          "url": "https://json.test",
          "timestamp": "0001-01-01 00:00:00",
          "http_status_code": 123,
          "response_time_ms": 456
        }"""
        )

    def test_deserializes_from_json(self):
        assert UrlProbe(
            url="https://json.test",
            timestamp=datetime.min,
            http_status_code=123,
            response_time_ms=456,
        ) == UrlProbe.from_json(
            """{
          "url": "https://json.test",
          "timestamp": "0001-01-01 00:00:00",
          "http_status_code": 123,
          "response_time_ms": 456
        }"""
        )

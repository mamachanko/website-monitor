import json
from datetime import datetime

import pytest

from website_monitor.url_probe import UrlProbe


class TestUrlProbe:
    @pytest.mark.parametrize("url", ["https://example.com", "https://httpbin.org"])
    def test_has_url(self, url):
        result = UrlProbe.probe(url)
        assert result.url == url

    def test_records_utc_now_as_timestamp(self):
        before = datetime.utcnow()
        result = UrlProbe.probe("https://httpbin.org/status/200")
        after = datetime.utcnow()

        assert before < result.timestamp < after

    @pytest.mark.parametrize("http_status_code", [200, 400])
    def test_has_status_code(self, http_status_code):
        result = UrlProbe.probe("https://httpbin.org/status/%s" % http_status_code)
        assert result.http_status_code == http_status_code

    @pytest.mark.parametrize("delay_s", [0.1, 2])
    def test_measures_response_time(self, delay_s):
        # This would be better tested against an in-process HTTP server.
        # This is a large margin of error and a flaky test.
        margin_ms = 1000
        at_least = (delay_s * 1000) - margin_ms
        at_most = (delay_s * 1000) + margin_ms

        result = UrlProbe.probe("https://httpbin.org/delay/%s" % delay_s)

        assert at_least < result.response_time_ms < at_most

    def test_serializes_to_json(self):
        assert json.loads(
            UrlProbe(
                url="https://example.com",
                timestamp=datetime.min,
                http_status_code=123,
                response_time_ms=456,
            ).json
        ) == json.loads(
            """{
          "url": "https://example.com",
          "timestamp": "0001-01-01 00:00:00",
          "http_status_code": 123,
          "response_time_ms": 456
        }"""
        )

    def test_deserializes_from_json(self):
        assert UrlProbe(
            url="https://example.com",
            timestamp=datetime.min,
            http_status_code=123,
            response_time_ms=456,
        ) == UrlProbe.from_json(
            """{
          "url": "https://example.com",
          "timestamp": "0001-01-01 00:00:00",
          "http_status_code": 123,
          "response_time_ms": 456
        }"""
        )

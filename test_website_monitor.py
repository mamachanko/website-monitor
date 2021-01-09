import json
from datetime import datetime

import pytest

from website_monitor import consume_and_write
from website_monitor import env
from website_monitor import probe_and_publish
from website_monitor.repository import Repository
from website_monitor.stats import Stats
from website_monitor.url_probe import UrlProbe


@pytest.fixture
def repository():
    repository = Repository(env.require_env("WM_DB_CONNECTION_STRING"))
    repository.setup()
    repository.delete_all()
    return repository


class TestIntegration:

    def test_probes_get_published_consumed_and_written(self, repository):
        assert repository.get_stats() == []

        probe_and_publish.main()
        probe_and_publish.main()

        consume_and_write.main()

        assert len(repository.find_all()) == 2
        assert len(repository.get_stats()) == 1


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
        assert json.loads(UrlProbe(
            url="https://example.com",
            timestamp=datetime.min,
            http_status_code=123,
            response_time_ms=456
        ).json) == json.loads("""{
          "url": "https://example.com",
          "timestamp": "0001-01-01 00:00:00",
          "http_status_code": 123,
          "response_time_ms": 456
        }""")

    def test_deserializes_from_json(self):
        assert UrlProbe(
            url="https://example.com",
            timestamp=datetime.min,
            http_status_code=123,
            response_time_ms=456
        ) == UrlProbe.from_json("""{
          "url": "https://example.com",
          "timestamp": "0001-01-01 00:00:00",
          "http_status_code": 123,
          "response_time_ms": 456
        }""")


class TestRepository:

    def test_saves_and_retrieves_url_probes(self, repository: Repository):
        url_probe = UrlProbe(
            url="https://example.com",
            timestamp=datetime.utcnow(),
            http_status_code=123,
            response_time_ms=456
        )

        repository.save([url_probe])

        assert repository.find_all() == [url_probe]

    def test_retrieves_no_url_probes(self, repository: Repository):
        assert repository.find_all() == []

    def test_reports_stats_without_variation(self, repository: Repository):
        repository.save(self.create_url_probes(
            *[1000 for _ in range(100)],
            url="https://example.com",
            timestamp=datetime.utcnow(),
            http_status_code=200
        ))

        stats = repository.get_stats()

        assert stats == [
            Stats(
                url="https://example.com",
                probes=100,
                p50_ms=10.0,
                p95_ms=10.0,
                p99_ms=10.0,
            )
        ]

    def test_reports_stats_with_variation(self, repository: Repository):
        repository.save(self.create_url_probes(
            *[1000, 2000, 3000],
            url="https://httpbin.org",
            timestamp=datetime.utcnow(),
            http_status_code=200
        ))

        stats = repository.get_stats()

        assert stats == [
            Stats(
                url="https://httpbin.org",
                probes=3,
                p50_ms=1000.0,
                p95_ms=2900.0,
                p99_ms=2980.0,
            )
        ]

    def create_url_probes(*response_times_ms: list[int], url: str, timestamp: datetime, http_status_code: int) \
            -> list[UrlProbe]:
        return [UrlProbe(
            url=url,
            timestamp=timestamp,
            http_status_code=http_status_code,
            response_time_ms=response_time_ms
        ) for response_time_ms in response_times_ms]


class TestStream:

    def test_fails(self):
        assert False

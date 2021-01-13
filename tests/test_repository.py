from datetime import datetime

from website_monitor.repository import Repository
from website_monitor.stats import Stats
from website_monitor.url_probe import UrlProbe


class TestRepository:
    def test_saves_and_retrieves_url_probes(self, repository: Repository):
        url_probe = UrlProbe(
            url="https://example.com",
            timestamp=datetime.utcnow(),
            http_status_code=123,
            response_time_ms=456,
        )

        repository.save([url_probe])

        assert repository.find_all() == [url_probe]

    def test_retrieves_no_url_probes(self, repository: Repository):
        assert repository.find_all() == []

    def test_reports_stats_without_variation(self, repository: Repository):
        repository.save(
            self.create_url_probes(
                *[1000 for _ in range(100)],
                url="https://example.com",
                timestamp=datetime.utcnow(),
                http_status_code=200
            )
        )

        stats = repository.get_stats()

        assert stats == [
            Stats(
                url="https://example.com",
                probes=100,
                p50_ms=1000.0,
                p95_ms=1000.0,
                p99_ms=1000.0,
            )
        ]

    def test_reports_stats_with_variation(self, repository: Repository):
        repository.save(
            self.create_url_probes(
                *[1000, 2000, 3000],
                url="https://httpbin.org",
                timestamp=datetime.utcnow(),
                http_status_code=200
            )
        )

        stats = repository.get_stats()

        assert stats == [
            Stats(
                url="https://httpbin.org",
                probes=3,
                p50_ms=2000.0,
                p95_ms=2900.0,
                p99_ms=2980.0,
            )
        ]

    def create_url_probes(
        self,
        *response_times_ms: list[int],
        url: str,
        timestamp: datetime,
        http_status_code: int
    ) -> list[UrlProbe]:
        return [
            UrlProbe(
                url=url,
                timestamp=timestamp,
                http_status_code=http_status_code,
                response_time_ms=response_time_ms,
            )
            for response_time_ms in response_times_ms
        ]

from datetime import datetime

import pytest

from website_monitor import consume_and_write, database, url_probe
from website_monitor import env
from website_monitor import probe_and_publish


@pytest.fixture
def db():
    db_connection_string = env.require_env("WM_DB_CONNECTION_STRING")
    db = database.Database(db_connection_string)
    db.setup()
    db.delete_all()
    return db


class TestIntegration:

    def test_probes_get_published_consumed_and_written(self, db):
        assert len(db.find_all()) == 0

        probe_and_publish.main()
        probe_and_publish.main()

        consume_and_write.main()

        assert len(db.find_all()) == 2


class TestUrlProbe:

    @pytest.mark.parametrize("url", ["https://example.com", "https://httpbin.org"])
    def test_has_url(self, url):
        result = url_probe.probe_url(url)
        assert result.url == url

    def test_records_utc_now_as_timestamp(self):
        before = datetime.utcnow()
        result = url_probe.probe_url("https://httpbin.org/status/200")
        after = datetime.utcnow()

        assert before < datetime.fromisoformat(result.timestamp) < after

    @pytest.mark.parametrize("http_status_code", [200, 400])
    def test_has_status_code(self, http_status_code):
        result = url_probe.probe_url("https://httpbin.org/status/%s" % http_status_code)
        assert result.http_status_code == http_status_code

    @pytest.mark.parametrize("delay_s", [0.1, 2])
    def test_measures_response_time(self, delay_s):
        # This would be better tested against in in-process http server.
        # This is a large margin of error and a flaky test.
        margin_ms = 1000
        min = (delay_s * 1000) - margin_ms
        max = (delay_s * 1000) + margin_ms

        result = url_probe.probe_url("https://httpbin.org/delay/%s" % delay_s)

        assert min < result.response_time_ms < max


class TestDatabase:

    def test_fails(self):
        assert False


class TestStream:

    def test_fails(self):
        assert False

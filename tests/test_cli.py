import json

import pytest
from click.testing import CliRunner

from website_monitor import env
from website_monitor.cli import wm
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic


def assert_url_stats_match(url_stats: dict, probes: int, url: str):
    assert url_stats["url"] == url, url_stats
    assert url_stats["probes"] == probes, url_stats
    assert 10 < url_stats["p50_ms"] < 2000, url_stats
    assert type(url_stats["p50_ms"]) == float, url_stats
    assert 10 < url_stats["p95_ms"] < 2000, url_stats
    assert type(url_stats["p95_ms"]) == float, url_stats
    assert 10 < url_stats["p99_ms"] < 2000, url_stats
    assert type(url_stats["p99_ms"]) == float, url_stats


class TestCLI:
    def test_no_stats_when_no_url_has_been_probed(self, repository):
        result = CliRunner().invoke(
            wm,
            [
                "stats",
                f"--db-connection-string={repository.connection_string}",
            ],
        )
        assert result.exit_code == 0, result.exception
        assert json.loads(result.output) == json.loads('{"stats": []}')

    def test_probes_get_published_and_flushed_and_accounted_for(
        self, repository: Repository, stream_topic: StreamTopic
    ):
        test_url_once = "https://httpbin.org/status/201"
        test_url_twice = "https://httpbin.org/status/200"

        runner = CliRunner()

        # When probing a URL once
        result = runner.invoke(
            wm,
            [
                "probe",
                f"--url={test_url_once}",
                f"--bootstrap-server={stream_topic.bootstrap_servers}",
                f"--topic={stream_topic.topic}",
                f"--ssl-cafile={stream_topic.ssl_cafile}",
                f"--ssl-certfile={stream_topic.ssl_certfile}",
                f"--ssl-keyfile={stream_topic.ssl_keyfile}",
            ],
        )
        assert result.exit_code == 0, result.exception

        # And when probing another URL twice
        for _ in range(2):
            result = runner.invoke(
                wm,
                [
                    "probe",
                    f"--url={test_url_twice}",
                    f"--bootstrap-server={stream_topic.bootstrap_servers}",
                    f"--topic={stream_topic.topic}",
                    f"--ssl-cafile={stream_topic.ssl_cafile}",
                    f"--ssl-certfile={stream_topic.ssl_certfile}",
                    f"--ssl-keyfile={stream_topic.ssl_keyfile}",
                ],
            )
            assert result.exit_code == 0, result.exception

        # And when flushing the results
        result = runner.invoke(
            wm,
            [
                "flush",
                f"--db-connection-string={repository.connection_string}",
                f"--bootstrap-server={stream_topic.bootstrap_servers}",
                f"--topic={stream_topic.topic}",
                f"--consumer-group-id={env.require_env('WM_STREAM_CONSUMER_GROUP_ID')}",
                f"--ssl-cafile={stream_topic.ssl_cafile}",
                f"--ssl-certfile={stream_topic.ssl_certfile}",
                f"--ssl-keyfile={stream_topic.ssl_keyfile}",
            ],
        )
        assert result.exit_code == 0, result.exception

        # Then the stats for both URLs are being returned as expected
        result = runner.invoke(
            wm,
            [
                "stats",
                f"--db-connection-string={repository.connection_string}",
            ],
        )
        assert result.exit_code == 0, result.exception
        stats = json.loads(result.output)
        assert len(stats["stats"]) == 2, stats
        # This test is flaky.
        assert_url_stats_match(stats["stats"][1], 1, test_url_once)
        assert_url_stats_match(stats["stats"][0], 2, test_url_twice)

    @pytest.mark.parametrize(
        "subcommand,ssl_file_option",
        [
            ("probe", "--ssl-cafile"),
            ("probe", "--ssl-certfile"),
            ("probe", "--ssl-keyfile"),
            ("flush", "--ssl-cafile"),
            ("flush", "--ssl-certfile"),
            ("flush", "--ssl-keyfile"),
        ],
    )
    def test_subcommand_fails_when_ssl_file_does_not_exist(
        self, subcommand, ssl_file_option
    ):
        runner = CliRunner()
        result = runner.invoke(
            wm,
            [
                subcommand,
                ssl_file_option + "=this-file-does-not-exist",
            ],
        )
        assert result.exit_code != 0, result
        assert "Path 'this-file-does-not-exist' does not exist" in result.output, result

import json

import pytest
from click.testing import CliRunner

from website_monitor import env
from website_monitor.cli import wm
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic


def run(*args):
    result = CliRunner().invoke(
        wm,
        args,
    )
    assert result.exit_code == 0, result.exception
    return result


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
    def test_no_stats_when_no_url_has_been_probed(
        self, repository: Repository, stream_topic: StreamTopic
    ):
        result = run(
            "stats",
            f"--db-connection-string={env.require_env('WM_DB_CONNECTION_STRING')}",
        )
        assert json.loads(result.output) == json.loads('{"stats": []}')

    def test_probes_get_published_and_flushed_and_accounted_for(
        self, repository: Repository, stream_topic: StreamTopic
    ):
        # Given all the required configuration
        test_url_once = "https://httpbin.org/status/201"
        test_url_twice = "https://httpbin.org/status/200"
        db_connection_string = env.require_env("WM_DB_CONNECTION_STRING")
        bootstrap_server = env.require_env("WM_STREAM_BOOTSTRAP_SERVERS")
        stream_topic = env.require_env("WM_STREAM_TOPIC")
        ssl_cafile = env.require_env("WM_STREAM_SSL_CA_FILE")
        ssl_certfile = env.require_env("WM_STREAM_SSL_CERT_FILE")
        ssl_keyfile = env.require_env("WM_STREAM_SSL_KEY_FILE")

        # When probing a URL once
        run(
            "probe",
            test_url_once,
            f"--bootstrap-server={bootstrap_server}",
            f"--topic={stream_topic}",
            f"--ssl-cafile={ssl_cafile}",
            f"--ssl-certfile={ssl_certfile}",
            f"--ssl-keyfile={ssl_keyfile}",
        )
        # And when probing another URL twice
        run(
            "probe",
            test_url_twice,
            f"--bootstrap-server={bootstrap_server}",
            f"--topic={stream_topic}",
            f"--ssl-cafile={ssl_cafile}",
            f"--ssl-certfile={ssl_certfile}",
            f"--ssl-keyfile={ssl_keyfile}",
        )
        run(
            "probe",
            test_url_twice,
            f"--bootstrap-server={bootstrap_server}",
            f"--topic={stream_topic}",
            f"--ssl-cafile={ssl_cafile}",
            f"--ssl-certfile={ssl_certfile}",
            f"--ssl-keyfile={ssl_keyfile}",
        )
        # And when flushing the results
        run(
            "flush",
            f"--db-connection-string={db_connection_string}",
            f"--bootstrap-server={bootstrap_server}",
            f"--topic={stream_topic}",
            f"--consumer-group-id={env.require_env('WM_STREAM_CONSUMER_GROUP_ID')}",
            f"--ssl-cafile={ssl_cafile}",
            f"--ssl-certfile={ssl_certfile}",
            f"--ssl-keyfile={ssl_keyfile}",
        )

        # Then the stats for both URLs are being returned as expected
        result = run(
            "stats",
            f"--db-connection-string={db_connection_string}",
        )
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

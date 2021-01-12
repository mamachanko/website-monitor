from textwrap import dedent

from website_monitor.env import require_env
from website_monitor.repository import Repository


def main():
    # fail fast if envs are missing
    db_connection_string = require_env("WM_DB_CONNECTION_STRING")

    repository = Repository(db_connection_string)
    print("results:")
    for i, stats in enumerate(repository.get_stats()):
        print(
            dedent(
                f"""
        - url: {stats.url}
          probes_total: {stats.probes}
          percentiles:
            p50_ms: {stats.p50_ms}
            p50_ms: {stats.p95_ms}
            p95_ms: {stats.p99_ms}
        """
            )
        )


if __name__ == "__main__":
    main()

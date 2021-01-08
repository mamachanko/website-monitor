import psycopg2

from website_monitor.env import require_env


def store(url_probes):
    db_connection_string = require_env("WM_DB_CONNECTION_STRING")
    with psycopg2.connect(db_connection_string) as conn:
        with conn.cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor,
                "insert into url_probes(url, timestamp, http_status_code, response_time_ms) values %s",
                [(up.url, up.timestamp, up.http_status_code, up.response_time_ms) for up in url_probes]
            )

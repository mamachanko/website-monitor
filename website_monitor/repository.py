import psycopg2
import psycopg2.extras

from website_monitor.stats import Stats
from website_monitor.url_probe import UrlProbe


class Repository:
    """
    The URL probe repository.

    Implements the repository pattern to hide the database interaction details.
    """

    def __init__(self, connection_string) -> None:
        self.connection_string = connection_string

    def setup(self):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    create table if not exists url_probes(
                        id bigserial primary key, 
                        url text not null,
                        timestamp timestamp not null,
                        http_status_code int not null,
                        response_time_ms int not null
                    );
                """
                )

    def delete_all(self):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("truncate table url_probes;")

    def find_all(self) -> list[UrlProbe]:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "select url, timestamp, http_status_code, response_time_ms from url_probes;"
                )
                return list(map(UrlProbe._make, cursor.fetchall()))

    def save(self, url_probes: list[UrlProbe]):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                psycopg2.extras.execute_values(
                    cursor,
                    "insert into url_probes(url, timestamp, http_status_code, response_time_ms) values %s",
                    [
                        (up.url, up.timestamp, up.http_status_code, up.response_time_ms)
                        for up in url_probes
                    ],
                )

    def get_stats(self) -> list[Stats]:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    select url,
                           count(*) as probes,
                           percentile_cont(0.5) within group (order by url_probes.response_time_ms)  as p50_ms,
                           percentile_cont(0.95) within group (order by url_probes.response_time_ms) as p95_ms,
                           percentile_cont(0.99) within group (order by url_probes.response_time_ms) as p99_ms
                    from url_probes
                    group by url;
                """
                )
                return list(map(Stats._make, cursor.fetchall()))

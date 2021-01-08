import psycopg2
import psycopg2.extras


class Database:

    def __init__(self, connection_string) -> None:
        self.connection_string = connection_string

    def setup(self):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    create table if not exists url_probes(
                        id bigserial primary key, 
                        url text not null,
                        timestamp timestamp not null,
                        http_status_code int not null,
                        response_time_ms int not null
                    );
                """)

    def clear(self):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("truncate table url_probes;")

    def find_all(self):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute("select * from url_probes;")
                return cursor.fetchall()

    def store(self, url_probes):
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                psycopg2.extras.execute_values(
                    cursor,
                    "insert into url_probes(url, timestamp, http_status_code, response_time_ms) values %s",
                    [(up.url, up.timestamp, up.http_status_code, up.response_time_ms) for up in url_probes]
                )

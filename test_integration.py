import psycopg2
import psycopg2.extras

from website_monitor import consume_and_write
from website_monitor import env
from website_monitor import probe_and_publish

DB_CONNECTION_STRING = env.require_env("WM_DB_CONNECTION_STRING")


def test_integration():
    setup_db()
    assert_db_contains_exactly_messages([])

    probe_and_publish.main()
    probe_and_publish.main()

    consume_and_write.main()

    assert len(retrieve()) == 2


def setup_db():
    with psycopg2.connect(DB_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                begin;
            
                create table if not exists url_probes(
                    id bigserial primary key, 
                    url text not null,
                    timestamp timestamp not null,
                    http_status_code int not null,
                    response_time_ms int not null
                );
            
                truncate table url_probes;
            
                commit;
            """)


def assert_db_contains_exactly_messages(messages):
    with psycopg2.connect(DB_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select http_status_code from url_probes;")
            assert list(map(lambda r: r[0], cursor.fetchall())) == messages


def retrieve():
    with psycopg2.connect(DB_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select * from url_probes;")
            return cursor.fetchall()

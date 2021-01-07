import kafka
import psycopg2
import psycopg2.extras

from website_monitor import probe_and_publish
from website_monitor.env import require_env
from website_monitor.url_probe import UrlProbeResult

STREAM_TOPIC = require_env("WM_STREAM_TOPIC")
STREAM_BOOTSTRAP_SERVERS = require_env("WM_STREAM_BOOTSTRAP_SERVERS")
STREAM_CONSUMER_GROUP_ID = require_env("WM_STREAM_CONSUMER_GROUP_ID")
STREAM_SSL_CA_FILE = require_env("WM_STREAM_SSL_CA_FILE")
STREAM_SSL_CERT_FILE = require_env("WM_STREAM_SSL_CERT_FILE")
STREAM_SSL_KEY_FILE = require_env("WM_STREAM_SSL_KEY_FILE")

DB_CONNECTION_STRING = require_env("WM_DB_CONNECTION_STRING")


# -- TEST SETUP --
# given a running website
# given a running Kafka instance
# given a running Postgres instance
# when running the website checker
# when running the database writer
# then (eventually) there will be results written to the database
# -- ~ --


def test_integration():
    setup_db()
    assert_db_contains_exactly_messages([])

    probe_and_publish.main()
    probe_and_publish.main()

    messages = consume_url_probe_results()
    store(messages)

    assert len(retrieve()) == 2
    # assert_db_contains_exactly_messages([message])


def consume_url_probe_results():
    consumer = kafka.KafkaConsumer(
        STREAM_TOPIC,
        group_id=STREAM_CONSUMER_GROUP_ID,
        bootstrap_servers=STREAM_BOOTSTRAP_SERVERS,
        security_protocol="SSL",
        ssl_cafile=STREAM_SSL_CA_FILE,
        ssl_certfile=STREAM_SSL_CERT_FILE,
        ssl_keyfile=STREAM_SSL_KEY_FILE,
        auto_offset_reset="earliest",
    )

    # With the help of:
    #   https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
    messages = []
    for _ in range(2):
        for _, ms in consumer.poll(timeout_ms=1000).items():
            for message in ms:
                messages.append(UrlProbeResult.from_json(message.value.decode("utf-8")))

    consumer.commit()
    consumer.close()

    return messages


def store(url_probe_results):
    with psycopg2.connect(DB_CONNECTION_STRING) as conn:
        with conn.cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor,
                "insert into url_probes(url, timestamp, http_status_code, response_time_ms) values %s",
                [(r.url, r.timestamp, r.http_status_code, r.response_time_ms) for r in url_probe_results]
            )


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


if __name__ == '__main__':
    test_integration()

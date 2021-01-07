import datetime
import json
import os

import kafka
import psycopg2
import psycopg2.extras
import requests


def require_env(env_name):
    env_value = os.environ.get(env_name)
    if not env_value:
        raise Exception("$%s is not set" % env_name)
    return env_value


URL = require_env("WM_URL")

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

# TODO make it a namedtuple
class UrlProbeResult:
    def __init__(self, url, timestamp, http_status_code, response_time_ms):
        self.response_time_ms = response_time_ms
        self.http_status_code = http_status_code
        self.timestamp = timestamp
        self.url = url

    def __str__(self) -> str:
        return json.dumps({
            "url": self.url,
            "timestamp": self.timestamp,
            "http_status_code": self.http_status_code,
            "response_time_ms": self.response_time_ms
        })

    @staticmethod
    def from_json(data):
        url_probe_result = json.loads(data)
        return UrlProbeResult(
            url=url_probe_result["url"],
            timestamp=url_probe_result["timestamp"],
            http_status_code=url_probe_result["http_status_code"],
            response_time_ms=url_probe_result["response_time_ms"],
        )


def test_integration():
    print(os.environ)

    setup_db()
    assert_db_contains_exactly_messages([])

    url_probe_result = probe_url(URL)
    publish_url_probe_result(url_probe_result)

    url_probe_result = probe_url(URL)
    publish_url_probe_result(url_probe_result)

    messages = consume_url_probe_results()
    store(messages)

    assert len(retrieve()) == 2
    # assert_db_contains_exactly_messages([message])


def probe_url(url):
    now = datetime.datetime.utcnow()
    response = requests.get(url, timeout=5000)
    return UrlProbeResult(
        url=url,
        timestamp=str(now),
        http_status_code=response.status_code,
        response_time_ms=int(response.elapsed.microseconds / 1000)
    )


def publish_url_probe_result(url_probe_result):
    producer = kafka.KafkaProducer(
        bootstrap_servers=STREAM_BOOTSTRAP_SERVERS,
        security_protocol="SSL",
        ssl_cafile=STREAM_SSL_CA_FILE,
        ssl_certfile=STREAM_SSL_CERT_FILE,
        ssl_keyfile=STREAM_SSL_KEY_FILE,
    )

    producer.send(STREAM_TOPIC, str(url_probe_result).encode("utf-8"))

    producer.flush()
    producer.close()


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

import datetime
import json

import kafka
import psycopg2
import psycopg2.extras
import requests

STREAM_TOPIC = "website_checker_test"
DB_CONNECTION_STRING = "postgres://avnadmin:xhy2rtzbyrk14cit@35.198.110.182:26728/website_monitor_test?sslmode=require"


# -- TEST SETUP --
# given a running Kafka instance
#   TODO
# given a running website
#   TODO
#   assuming https://httpbin.com
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
    setup_db()
    assert_db_contains_exactly_messages([])

    url_probe_result = probe_url("https://httpbin.org/status/200")
    publish_url_probe_result(url_probe_result)

    url_probe_result = probe_url("https://httpbin.org/status/400")
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


def publish_url_probe_result(message):
    producer = kafka.KafkaProducer(
        bootstrap_servers="stream-sugardubz-dc85.aivencloud.com:26730",
        security_protocol="SSL",
        ssl_cafile="/Users/floater/workspace/aiven-interview/stream.pem",
        ssl_certfile="/Users/floater/workspace/aiven-interview/stream.cert",
        ssl_keyfile="/Users/floater/workspace/aiven-interview/stream.key",
    )

    def on_send_success(record_metadata):
        print("published %s:%d:%d" % (
            record_metadata.topic, record_metadata.partition, record_metadata.offset))

    print("publishing ...")
    producer.send(STREAM_TOPIC, str(message).encode("utf-8")).add_callback(on_send_success)

    producer.flush()
    producer.close()
    print("done.")


def consume_url_probe_results():
    consumer = kafka.KafkaConsumer(
        STREAM_TOPIC,
        group_id="my-group",
        bootstrap_servers="stream-sugardubz-dc85.aivencloud.com:26730",
        security_protocol="SSL",
        ssl_cafile="/Users/floater/workspace/aiven-interview/stream.pem",
        ssl_certfile="/Users/floater/workspace/aiven-interview/stream.cert",
        ssl_keyfile="/Users/floater/workspace/aiven-interview/stream.key",
        auto_offset_reset="earliest",
    )

    print("consuming ...")

    # https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
    messages = []
    for _ in range(2):
        for _, ms in consumer.poll(timeout_ms=1000).items():
            for message in ms:
                print("Received: {}".format(message.value))
                messages.append(UrlProbeResult.from_json(message.value.decode("utf-8")))

    consumer.commit()
    consumer.close()
    print("done.")

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

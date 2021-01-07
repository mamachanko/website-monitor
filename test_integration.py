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


def test_integration():
    setup_db()
    assert_db_contains_exactly_messages([])

    url_probe_result = probe_url("https://httpbin.org/status/200")
    publish(json.dumps(url_probe_result))

    url_probe_result = probe_url("https://httpbin.org/status/400")
    publish(json.dumps(url_probe_result))

    messages = consume()
    store(messages)

    assert len(retrieve()) == 2
    # assert_db_contains_exactly_messages([message])


def probe_url(url):
    now = datetime.datetime.utcnow()
    response = requests.get(url, timeout=5000)
    return {
        "timestamp": str(now),
        "http_status_code": response.status_code,
        "url": url,
        "response_time_ms": int(response.elapsed.microseconds / 1000)
    }


def publish(message):
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
    producer.send(STREAM_TOPIC, message.encode("utf-8")).add_callback(on_send_success)

    producer.flush()
    producer.close()
    print("done.")


def consume():
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
                messages.append(json.loads(message.value.decode("utf-8")))

    consumer.commit()
    consumer.close()
    print("done.")

    return messages


def store(url_probe_results):
    db_connection = psycopg2.connect(DB_CONNECTION_STRING)
    db_cursor = db_connection.cursor()
    psycopg2.extras.execute_values(
        db_cursor,
        "insert into url_probes(url, timestamp, http_status_code, response_time_ms) values %s",
        [(r["url"], r["timestamp"], r["http_status_code"], r["response_time_ms"]) for r in url_probe_results]
    )
    db_connection.commit()
    db_cursor.close()
    db_connection.close()


def setup_db():
    db_connection = psycopg2.connect(DB_CONNECTION_STRING)
    db_cursor = db_connection.cursor()
    # {
    #     "timestamp": now.timestamp(),
    #     "http_status_code": response.status_code,
    #     "url": url,
    #     "response_time_ms": int(response.elapsed.microseconds / 1000)
    # }
    db_cursor.execute("""
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
    db_connection.commit()
    db_cursor.close()
    db_connection.close()


def assert_db_contains_exactly_messages(messages):
    db_connection = psycopg2.connect(DB_CONNECTION_STRING)
    db_cursor = db_connection.cursor()
    db_cursor.execute("select http_status_code from url_probes;")
    db_connection.commit()
    assert list(map(lambda r: r[0], db_cursor.fetchall())) == messages
    db_cursor.close()
    db_connection.close()


def retrieve():
    db_connection = psycopg2.connect(DB_CONNECTION_STRING)
    db_cursor = db_connection.cursor()
    db_cursor.execute("select * from url_probes;")
    db_connection.commit()
    url_probes = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return url_probes


if __name__ == '__main__':
    test_integration()

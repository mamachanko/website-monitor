import kafka

from website_monitor.env import require_env


def publish(message):
    producer = kafka.KafkaProducer(
        bootstrap_servers=require_env("WM_STREAM_BOOTSTRAP_SERVERS"),
        security_protocol="SSL",
        ssl_cafile=require_env("WM_STREAM_SSL_CA_FILE"),
        ssl_certfile=require_env("WM_STREAM_SSL_CERT_FILE"),
        ssl_keyfile=require_env("WM_STREAM_SSL_KEY_FILE"),
    )

    producer.send(require_env("WM_STREAM_TOPIC"), message.encode("utf-8"))

    producer.flush()
    producer.close()


def consume():
    consumer = kafka.KafkaConsumer(
        require_env("WM_STREAM_TOPIC"),
        group_id=require_env("WM_STREAM_CONSUMER_GROUP_ID"),
        bootstrap_servers=require_env("WM_STREAM_BOOTSTRAP_SERVERS"),
        security_protocol="SSL",
        ssl_cafile=require_env("WM_STREAM_SSL_CA_FILE"),
        ssl_certfile=require_env("WM_STREAM_SSL_CERT_FILE"),
        ssl_keyfile=require_env("WM_STREAM_SSL_KEY_FILE"),
        api_version=(2,),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    # Inspired by
    # https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka

    records: list[str] = []
    poll_count = 0
    while poll_count := poll_count + 1:
        poll = consumer.poll(timeout_ms=1000, max_records=10)

        # poll at least twice and until there are no more records
        if poll_count > 1 and len(poll) == 0:
            break

        records += map(lambda r: r.value.decode("utf-8"), poll.values())

    def commit() -> None:
        consumer.commit()
        consumer.close()

    return records, commit

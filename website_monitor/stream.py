import kafka

from website_monitor.env import require_env
from website_monitor.url_probe import UrlProbe


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

    url_probes: list[UrlProbe] = []
    poll_count = 0
    while poll_count := poll_count + 1:
        poll = consumer.poll(timeout_ms=1000, max_records=10)

        # poll at least twice and until there are no more records
        if poll_count > 1 and len(poll) == 0:
            break

        for raw_url_probes in poll.values():
            for url_probe_json in raw_url_probes:
                url_probe = UrlProbe.from_json(url_probe_json.value.decode("utf-8"))
                url_probes.append(url_probe)

    def commit():
        consumer.commit()
        consumer.close()

    return url_probes, commit

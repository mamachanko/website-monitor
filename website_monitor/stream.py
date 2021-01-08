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
        api_version=(0, 10, 2),
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    # Inspired by
    # https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka
    url_probes = []
    for _ in range(2):
        for raw_url_probes in consumer.poll(timeout_ms=1000).values():
            for url_probe_json in raw_url_probes:
                url_probe = UrlProbe.from_json(url_probe_json.value.decode("utf-8"))
                url_probes.append(url_probe)

    consumer.commit()
    consumer.close()

    return url_probes

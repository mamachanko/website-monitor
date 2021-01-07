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

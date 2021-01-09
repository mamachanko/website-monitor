from typing import Tuple, Callable

import kafka


def publish(message: str, bootstrap_servers: str, ssl_cafile: str, ssl_certfile: str, ssl_keyfile: str,
            topic: str) -> None:
    producer = kafka.KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SSL",
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )

    producer.send(topic, message.encode("utf-8"))

    producer.flush()
    producer.close()


def consume(topic: str, bootstrap_servers: str, group_id: str, ssl_cafile: str,
            ssl_certfile: str, ssl_keyfile: str) -> Tuple[list[str], Callable[[], None]]:
    consumer = kafka.KafkaConsumer(
        topic,
        group_id=group_id,
        bootstrap_servers=bootstrap_servers,
        security_protocol="SSL",
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
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

        for polled_records in poll.values():
            for raw_record in polled_records:
                records.append(raw_record.value.decode("utf-8"))

    def commit() -> None:
        consumer.commit()
        consumer.close()

    return records, commit

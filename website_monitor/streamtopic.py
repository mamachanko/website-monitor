from typing import Tuple, Callable

import kafka


class StreamTopic:
    """
    Represents a Kafka stream topic which messages can be published to and consumed from.
    """

    _security_protocol = "SSL"

    # An attempt to resolve the frequent NoBrokersAvailable exception.
    # https://github.com/dpkp/kafka-python/issues/1308
    _api_version = (2,)

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        ssl_cafile: str,
        ssl_certfile: str,
        ssl_keyfile: str,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.ssl_certfile = ssl_certfile
        self.ssl_cafile = ssl_cafile
        self.ssl_keyfile = ssl_keyfile

    def publish(self, message: str) -> None:
        producer = self._create_producer()

        producer.send(self.topic, message.encode("utf-8"))

        producer.flush()
        producer.close()

    def consume(self, group_id: str) -> Tuple[list[str], Callable[[], None]]:
        """
        Consume messages using the given group_id.

        Returns messages and a commit callback.

        (Inspired by https://help.aiven.io/en/articles/489572-getting-started-with-aiven-kafka)
        """
        consumer = self._create_consumer(group_id)

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

    def exhaust(self, group_id: str) -> None:
        (_, commit) = self.consume(group_id)
        commit()

    def _create_producer(self):
        return kafka.KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            security_protocol=self._security_protocol,
            ssl_cafile=self.ssl_cafile,
            ssl_certfile=self.ssl_certfile,
            ssl_keyfile=self.ssl_keyfile,
        )

    def _create_consumer(self, group_id):
        return kafka.KafkaConsumer(
            self.topic,
            group_id=group_id,
            bootstrap_servers=self.bootstrap_servers,
            security_protocol="SSL",
            ssl_cafile=self.ssl_cafile,
            ssl_certfile=self.ssl_certfile,
            ssl_keyfile=self.ssl_keyfile,
            api_version=self._api_version,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )

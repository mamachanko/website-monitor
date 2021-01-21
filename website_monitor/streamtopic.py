from contextlib import contextmanager

import kafka


class StreamTopic:
    """
    Represents a Kafka stream topic which messages can be published to and consumed from.
    """

    # An attempt to resolve the frequent NoBrokersAvailable exception.
    # https://github.com/dpkp/kafka-python/issues/1308
    _api_version = (2,)

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        ssl: bool = False,
        ssl_cafile: str = None,
        ssl_certfile: str = None,
        ssl_keyfile: str = None,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.ssl = ssl
        self.ssl_certfile = ssl_certfile
        self.ssl_cafile = ssl_cafile
        self.ssl_keyfile = ssl_keyfile

    def publish(self, message: str) -> None:
        producer = self._create_producer()

        producer.send(self.topic, message.encode("utf-8"))

        producer.flush()
        producer.close()

    @contextmanager
    def consume(self, group_id: str) -> list[str]:
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

        yield records

        consumer.commit()
        consumer.close()

    def _create_producer(self):
        return kafka.KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            api_version=self._api_version,
            security_protocol="SSL" if self.ssl else "PLAINTEXT",
            ssl_cafile=self.ssl_cafile,
            ssl_certfile=self.ssl_certfile,
            ssl_keyfile=self.ssl_keyfile,
        )

    def _create_consumer(self, group_id):
        return kafka.KafkaConsumer(
            self.topic,
            group_id=group_id,
            bootstrap_servers=self.bootstrap_servers,
            api_version=self._api_version,
            security_protocol="SSL" if self.ssl else "PLAINTEXT",
            ssl_cafile=self.ssl_cafile,
            ssl_certfile=self.ssl_certfile,
            ssl_keyfile=self.ssl_keyfile,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )

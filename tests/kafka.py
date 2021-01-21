import tarfile
import time
from io import BytesIO
from textwrap import dedent

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready


class KafkaContainer(DockerContainer):
    """
    Inspired by:
    https://github.com/ash1425/testcontainers-python/commit/f6bde6fdc27cc5e5c4fe2babe3aa4a67ec5d59d9#diff-8ef539360409ebc9b1a0ede86a732c54ee8116f9c3d7214599eacbc87f87a0b8
    """

    DEFAULT_IMAGE = "confluentinc/cp-kafka:5.4.3"
    DEFAULT_PORT = 9093
    START_SCRIPT_PATH = "/testcontainers-start-kafka.sh"

    def __init__(self, image=DEFAULT_IMAGE, port_to_expose=DEFAULT_PORT):
        super(KafkaContainer, self).__init__(image)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        self.with_env(
            "KAFKA_LISTENERS",
            "PLAINTEXT://0.0.0.0:{},BROKER://0.0.0.0:9092".format(port_to_expose),
        )
        self.with_env(
            "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP",
            "BROKER:PLAINTEXT,PLAINTEXT:PLAINTEXT",
        )
        self.with_env("KAFKA_INTER_BROKER_LISTENER_NAME", "BROKER")

        self.with_env("KAFKA_BROKER_ID", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "1")
        self.with_env("KAFKA_OFFSETS_TOPIC_NUM_PARTITIONS", "1")
        self.with_env("KAFKA_LOG_FLUSH_INTERVAL_MESSAGES", "10000000")
        self.with_env("KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS", "0")

    def get_bootstrap_server(self):
        return f"{self.get_container_host_ip()}:{self.get_exposed_port(self.port_to_expose)}"

    def start(self):
        self.with_command(
            f'sh -c "while [ ! -f {self.START_SCRIPT_PATH} ]; do sleep 0.1; done; sh {self.START_SCRIPT_PATH}"'
        )
        super().start()
        self._start_kafka()
        self.is_ready()
        return self

    def _start_kafka(self):
        start_script = (
            dedent(
                f"""
            #!/usr/bin/env bash

            set -e

            echo "clientPort=2181" > zookeeper.properties
            echo "dataDir=/var/lib/zookeeper/data" >> zookeeper.properties
            echo "dataLogDir=/var/lib/zookeeper/log" >> zookeeper.properties

            zookeeper-server-start zookeeper.properties &

            export KAFKA_ZOOKEEPER_CONNECT="localhost:2181"
            KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://localhost:{self.get_exposed_port(self.port_to_expose)},BROKER://$(hostname -i):9092"
            export KAFKA_ADVERTISED_LISTENERS

            . /etc/confluent/docker/bash-config

            /etc/confluent/docker/configure
            /etc/confluent/docker/launch
        """
            )
            .strip()
            .encode("utf-8")
        )

        self.copy(start_script, self.START_SCRIPT_PATH)

    def copy(self, content: bytes, path: str):
        with BytesIO() as archive, tarfile.TarFile(fileobj=archive, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=path)
            tarinfo.size = len(content)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, BytesIO(content))
            archive.seek(0)
            self.get_wrapped_container().put_archive("/", archive)

    @wait_container_is_ready()
    def is_ready(self) -> bool:
        consumer = KafkaConsumer(
            group_id="test",
            bootstrap_servers=self.get_bootstrap_server(),
        )
        if not consumer.topics():
            raise KafkaError(
                f"Could not connect to Kafka at {self.get_bootstrap_server()}"
            )

        return True

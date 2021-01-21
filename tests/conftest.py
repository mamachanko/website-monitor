import uuid

import pytest
from testcontainers.postgres import PostgresContainer

from tests.httpbin import Httpbin
from tests.kafka import KafkaContainer
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic


@pytest.fixture(scope="session")
def httpbin() -> Httpbin:
    with Httpbin() as httpbin:
        yield httpbin


@pytest.fixture(scope="session")
def kafka() -> KafkaContainer:
    with KafkaContainer() as kafka:
        yield kafka


@pytest.fixture(scope="session")
def db_connection_string() -> str:
    with PostgresContainer("postgres:13.1-alpine") as postgres:
        yield (
            "{sqldialect}://{username}:{password}@{host}:{port}/{db}".format(
                sqldialect="postgresql",
                username=postgres.POSTGRES_USER,
                password=postgres.POSTGRES_PASSWORD,
                host=postgres.get_container_host_ip(),
                port=postgres.get_exposed_port(postgres.port_to_expose),
                db=postgres.POSTGRES_DB,
            )
        )


@pytest.fixture
def repository(db_connection_string: str) -> Repository:
    repository = Repository(connection_string=db_connection_string)
    repository.setup()
    repository.delete_all()
    return repository


@pytest.fixture
def topic() -> str:
    return f"test-{uuid.uuid4()}"


@pytest.fixture
def stream_topic(kafka: KafkaContainer, topic: str) -> StreamTopic:
    return StreamTopic(
        topic=topic,
        bootstrap_servers=kafka.get_bootstrap_server(),
    )

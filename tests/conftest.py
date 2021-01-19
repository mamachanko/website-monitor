import pytest
from testcontainers.postgres import PostgresContainer

from tests.httpbin import Httpbin
from website_monitor import env
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic


@pytest.fixture(scope="session")
def httpbin() -> Httpbin:
    with Httpbin() as httpbin:
        yield httpbin


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
def repository(db_connection_string) -> Repository:
    repository = Repository(connection_string=db_connection_string)
    repository.setup()
    repository.delete_all()
    return repository


@pytest.fixture
def stream_topic() -> StreamTopic:
    stream_topic = StreamTopic(
        topic=env.require_env("WM_STREAM_TOPIC"),
        bootstrap_servers=env.require_env("WM_STREAM_BOOTSTRAP_SERVERS"),
        ssl_cafile=env.require_env("WM_STREAM_SSL_CA_FILE"),
        ssl_certfile=env.require_env("WM_STREAM_SSL_CERT_FILE"),
        ssl_keyfile=env.require_env("WM_STREAM_SSL_KEY_FILE"),
    )
    stream_topic.exhaust(group_id=env.require_env("WM_STREAM_CONSUMER_GROUP_ID"))
    return stream_topic

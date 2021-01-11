import pytest

from website_monitor import env
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic


@pytest.fixture
def repository() -> Repository:
    repository = Repository(env.require_env("WM_DB_CONNECTION_STRING"))
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

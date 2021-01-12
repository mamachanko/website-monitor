from website_monitor.env import require_env
from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic
from website_monitor.url_probe import UrlProbe


def main():
    # fail fast if envs are missing
    db_connection_string = require_env("WM_DB_CONNECTION_STRING")
    bootstrap_servers = require_env("WM_STREAM_BOOTSTRAP_SERVERS")
    topic = require_env("WM_STREAM_TOPIC")
    group_id = require_env("WM_STREAM_CONSUMER_GROUP_ID")
    ssl_cafile = require_env("WM_STREAM_SSL_CA_FILE")
    ssl_certfile = require_env("WM_STREAM_SSL_CERT_FILE")
    ssl_keyfile = require_env("WM_STREAM_SSL_KEY_FILE")

    stream = StreamTopic(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )
    repository = Repository(db_connection_string)

    records, commit = stream.consume(group_id=group_id)
    repository.save(map(UrlProbe.from_json, records))
    commit()


if __name__ == "__main__":
    main()

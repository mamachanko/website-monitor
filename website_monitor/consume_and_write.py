from website_monitor.database import Database
from website_monitor.env import require_env
from website_monitor.stream import consume
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

    records, commit = consume(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        group_id=group_id,
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )
    db = Database(db_connection_string)
    db.save(map(UrlProbe.from_json, records))
    commit()


if __name__ == '__main__':
    main()

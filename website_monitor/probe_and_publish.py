from website_monitor.env import require_env
from website_monitor.stream import publish
from website_monitor.url_probe import probe_url


def main():
    # fail fast if envs are missing
    url = require_env("WM_URL")
    bootstrap_servers = require_env("WM_STREAM_BOOTSTRAP_SERVERS")
    topic = require_env("WM_STREAM_TOPIC")
    ssl_cafile = require_env("WM_STREAM_SSL_CA_FILE")
    ssl_certfile = require_env("WM_STREAM_SSL_CERT_FILE")
    ssl_keyfile = require_env("WM_STREAM_SSL_KEY_FILE")

    result = probe_url(url)
    publish(
        message=str(result),
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile
    )


if __name__ == '__main__':
    main()

import json

import click

from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic
from website_monitor.url_probe import UrlProbe


@click.group()
def wm():
    pass


@wm.command()
@click.option("-u", "--url", type=click.STRING, envvar="WM_URL", show_envvar=True)
@click.option(
    "-b",
    "--bootstrap-server",
    type=click.STRING,
    envvar="WM_STREAM_BOOTSTRAP_SERVER",
    show_envvar=True,
)
@click.option(
    "-t", "--topic", type=click.STRING, envvar="WM_STREAM_TOPIC", show_envvar=True
)
@click.option(
    "-ca",
    "--ssl-cafile",
    type=click.Path(exists=True),
    envvar="WM_STREAM_SSL_CA_FILE",
    show_envvar=True,
)
@click.option(
    "-ce",
    "--ssl-certfile",
    type=click.Path(exists=True),
    envvar="WM_STREAM_SSL_CERT_FILE",
    show_envvar=True,
)
@click.option(
    "-k",
    "--ssl-keyfile",
    type=click.Path(exists=True),
    envvar="WM_STREAM_SSL_KEY_FILE",
    show_envvar=True,
)
def probe(
    url: str,
    bootstrap_server: str,
    topic: str,
    ssl_cafile: str,
    ssl_certfile: str,
    ssl_keyfile: str,
):
    stream = StreamTopic(
        bootstrap_servers=bootstrap_server,
        topic=topic,
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )

    url_probe = UrlProbe.probe(url)
    stream.publish(message=url_probe.json)


@wm.command()
@click.option(
    "-d",
    "--db-connection-string",
    type=click.STRING,
    envvar="WM_DB_CONNECTION_STRING",
    show_envvar=True,
)
@click.option(
    "-b",
    "--bootstrap-server",
    type=click.STRING,
    envvar="WM_STREAM_BOOTSTRAP_SERVER",
    show_envvar=True,
)
@click.option(
    "-t", "--topic", type=click.STRING, envvar="WM_STREAM_TOPIC", show_envvar=True
)
@click.option(
    "-c",
    "--consumer-group-id",
    type=click.STRING,
    envvar="WM_STREAM_CONSUMER_GROUP_ID",
    show_envvar=True,
)
@click.option(
    "-ca",
    "--ssl-cafile",
    type=click.Path(exists=True),
    envvar="WM_STREAM_SSL_CA_FILE",
    show_envvar=True,
)
@click.option(
    "-ce",
    "--ssl-certfile",
    type=click.Path(exists=True),
    envvar="WM_STREAM_SSL_CERT_FILE",
    show_envvar=True,
)
@click.option(
    "-k",
    "--ssl-keyfile",
    type=click.Path(exists=True),
    envvar="WM_STREAM_SSL_KEY_FILE",
    show_envvar=True,
)
def flush(
    db_connection_string: str,
    bootstrap_server: str,
    topic: str,
    consumer_group_id: str,
    ssl_cafile: str,
    ssl_certfile: str,
    ssl_keyfile: str,
):
    stream = StreamTopic(
        bootstrap_servers=bootstrap_server,
        topic=topic,
        ssl_cafile=ssl_cafile,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )
    repository = Repository(db_connection_string)

    with stream.consume(group_id=consumer_group_id) as records:
        repository.save(map(UrlProbe.from_json, records))


@wm.command("stats")
@click.option(
    "-d",
    "--db-connection-string",
    type=click.STRING,
    envvar="WM_DB_CONNECTION_STRING",
    show_envvar=True,
)
def stats(db_connection_string: str):
    repository = Repository(db_connection_string)

    click.echo(
        json.dumps(
            {"stats": [s._asdict() for s in repository.get_stats()]},
            indent=2,
        )
    )

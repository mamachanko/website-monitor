import json

import click

from website_monitor.repository import Repository
from website_monitor.streamtopic import StreamTopic
from website_monitor.url_probe import UrlProbe


@click.group()
def wm():
    pass


@wm.command()
@click.argument("url", type=click.STRING)
@click.option("-b", "--bootstrap-server", type=click.STRING)
@click.option("-t", "--topic", type=click.STRING)
@click.option("-ca", "--ssl-cafile", type=click.Path(exists=True))
@click.option("-ce", "--ssl-certfile", type=click.Path(exists=True))
@click.option("-k", "--ssl-keyfile", type=click.Path(exists=True))
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
@click.option("-d", "--db-connection-string", type=click.STRING)
@click.option("-b", "--bootstrap-server", type=click.STRING)
@click.option("-t", "--topic", type=click.STRING)
@click.option("-c", "--consumer-group-id", type=click.STRING)
@click.option("-ca", "--ssl-cafile", type=click.Path(exists=True))
@click.option("-ce", "--ssl-certfile", type=click.Path(exists=True))
@click.option("-k", "--ssl-keyfile", type=click.Path(exists=True))
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

    records, commit = stream.consume(group_id=consumer_group_id)
    repository.save(map(UrlProbe.from_json, records))
    commit()


@wm.command("stats")
@click.option("-d", "--db-connection-string", type=click.STRING)
def stats(db_connection_string: str):
    repository = Repository(db_connection_string)

    click.echo(
        json.dumps(
            {"stats": [s._asdict() for s in repository.get_stats()]},
            indent=2,
        )
    )

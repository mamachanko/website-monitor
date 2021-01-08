import pytest

from website_monitor import consume_and_write, database
from website_monitor import env
from website_monitor import probe_and_publish


@pytest.fixture
def db():
    db_connection_string = env.require_env("WM_DB_CONNECTION_STRING")
    db = database.Database(db_connection_string)
    db.setup()
    db.delete_all()
    return db


def test_probes_get_published_consumed_and_written(db):
    assert len(db.find_all()) == 0

    probe_and_publish.main()
    probe_and_publish.main()

    consume_and_write.main()

    assert len(db.find_all()) == 2

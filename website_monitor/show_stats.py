from pprint import pprint

from website_monitor.env import require_env
from website_monitor.repository import Repository


def main():
    # fail fast if envs are missing
    db_connection_string = require_env("WM_DB_CONNECTION_STRING")

    repository = Repository(db_connection_string)
    stats = repository.get_stats()
    pprint(stats)


if __name__ == '__main__':
    main()

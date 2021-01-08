from website_monitor import stream, database, env
from website_monitor.url_probe import UrlProbe


def main():
    records, commit = stream.consume()
    db = database.Database(env.require_env("WM_DB_CONNECTION_STRING"))
    db.save(map(UrlProbe.from_json, records))
    commit()


if __name__ == '__main__':
    main()
    print("done.")

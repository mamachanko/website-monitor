from website_monitor import stream, database, env


def main():
    url_probes, commit = stream.consume()
    db = database.Database(env.require_env("WM_DB_CONNECTION_STRING"))
    db.store(url_probes)
    commit()


if __name__ == '__main__':
    main()
    print("done.")

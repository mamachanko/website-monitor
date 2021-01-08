from website_monitor import stream, database


def main():
    url_probes = stream.consume()
    database.store(url_probes)


if __name__ == '__main__':
    main()
    print("done.")

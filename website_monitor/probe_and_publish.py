from website_monitor.env import require_env
from website_monitor.stream import publish
from website_monitor.url_probe import probe_url


def main():
    result = probe_url(require_env("WM_URL"))
    publish(str(result))


if __name__ == '__main__':
    main()
    print("done.")

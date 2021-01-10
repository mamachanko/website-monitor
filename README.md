![tests](https://github.com/mamachanko/website-monitor/workflows/tests/badge.svg)

# Website Monitor

> A simple monitoring tool 🔭 to track response times and HTTP status for URLs using Kafka 🐞 and Postgres 🐘.

It has three components:

* 📞 Requesting a URL and publishing its HTTP status code, response time and a timestamp to a Kafka topic.
* 📒 Consuming results from a Kafka topic and writing them to a Postgres instance.
* 📊 Display of performance statistics for each URL with percentiles.

Each component is available as an executable module of the `website_monitor` package:

```shell
python -m website_monitor.probe_and_publish
python -m website_monitor.consume_and_write
python -m website_monitor.show_stats
```

Tested under Python 3.9.

## Configuration

The `website_monitor`'s components depend on environment variables namespaced within `WM_`:

```
WM_URL # the URL to be probed
WM_DB_CONNECTION_STRING # PostgreSQL connection string for storing results e.g. 'postgres://username:password@12.34.56.67/my-database'
WM_STREAM_BOOTSTRAP_SERVERS # one of the Kafka cluster's bootstrap servers and its port e.g. '12.34.56.78:1234'
WM_STREAM_TOPIC # the Kafka topic to publish results to and consume from
WM_STREAM_CONSUMER_GROUP_ID # the group id to read from and commit to the Kafka topic as
WM_STREAM_SSL_CA_FILE # the path to the Kafka SSL CA file
WM_STREAM_SSL_CERT_FILE # the path to the Kafka SSL certificate file
WM_STREAM_SSL_KEY_FILE # the path to the Kafka SSL key file
```

## Example

```shell
$ source <(cat <<EOF
WM_DB_CONNECTION_STRING=postgres://username:password@my-postgres:5432/website_monitor
WM_STREAM_TOPIC=website_monitor
WM_STREAM_BOOTSTRAP_SERVERS=my-kafka:1234
WM_STREAM_CONSUMER_GROUP_ID=website-monitor-consumers
WM_STREAM_SSL_CA_FILE=kafka.pem
WM_STREAM_SSL_CERT_FILE=kafka.cert
WM_STREAM_SSL_KEY_FILE=kafka.key
EOF
)
$ WM_URL=https://httpbin.org/delay/2 python -m website_monitor.probe_and_publish
$ for i in {1..10}; do
> WM_URL=https://httpbin.org/status/200 python -m website_monitor.probe_and_publish
> sleep 1;
> done
$ python -m website_monitor.consume_and_write
$ python -m website_monitor.show_stats
results:

- url: https://httpbin.org/delay/2
  probes_total: 1
  percentiles:
    p50_ms: 2464.0
    p50_ms: 2464.0
    p95_ms: 2464.0

- url: https://httpbin.org/status/200
  probes_total: 10
  percentiles:
    p50_ms: 462.0
    p50_ms: 2060.149999999998
    p95_ms: 3348.0300000000016

```

## Example deployment ☸️

See `example-deployment/` for an example deployment to Kubernetes. It runs periodic probes of a URL in one pod and
consumes the results from another.

## Design decisions, areas of improvement and known issues.

The `website_monitor` leaves it to the user to implement periodic probing of a URL. This can be viewed as a merit but
also as a drawback. For one, it lends itself well as a CLI and can be easily run periodically by wrapping it with a
Bash `for` or `while` loop. On the other hand it puts the burden on the deployment to run it periodically if that is
desired. However, platforms like Kubernetes have cron jobs. Alternatively, one could have implemented long-running
processes.

The use of Kafka is naïve and possibly wasteful. This is to be blamed on my ignorance of Kafka and its patterns.

Every component blocks until it's done. While this makes for easy testing and CLI usage it might not make for the most
efficient and performant design. Every invocation opens and closes a connection to Postgres or Kafka. This is possibly
wasteful.

All configuration happens through environment variables. This is great for configuration of deployments, but it can be
awkward to use as a CLI which purely depends on environment variables. It is particularly awkward to depend on
environment variables which contain paths (see `WM_STREAM_SSL_CA_FILE`, `WM_STREAM_SSL_CERT_FILE`
and `WM_STREAM_SSL_KEY_FILE`) as it coupling to the file system. Kubernetes' secrets allow to overcome the the issue by
mounting secrets as file.

The statistics list p50, p95 and p99 percentiles for response times per URL but do not factor in HTTP status code or
temporal distribution.

Logging is entirely absent.

The database schema contains a single table. There are no indexes. It is not optimized for a particular query pattern.
This is an area of improvement.

Initializing the schema of a new database needs to be done manually. However, with the given components it would be
easily automated.

The `website_monitor.repository.Repository` contains duplicated code within each CRUD operation. Each query result is
exploded into a `list` in memory. This is probably wasteful on memory and could be improved.

The tests are heavy on integration as they depend on out of process resources. They make real network requests and
expect a Postgres and Kafka instance to be available. This makes for slow tests which in turn provide a high level
of confidence.

The stream tests sometimes fail with `NoBrokersAvailable`. According
to [this kafka-python issue](https://github.com/dpkp/kafka-python/issues/1308)
is can be resolved by specifying the Kafka API version. I have not been able to succesfully resolve the issue. This is
pending.

Provisioning of a Postgres and Kafka instance (through [Aiven](https://aiven.io) for example) is not automated, as is
the configuration of the environment variables.

![tests](https://github.com/mamachanko/website-monitor/workflows/tests/badge.svg)
![Publish to PyPI](https://github.com/mamachanko/website-monitor/workflows/Publish%20to%20PyPI/badge.svg?branch=v0.0.4)
![codeql](https://github.com/mamachanko/website-monitor/workflows/CodeQL/badge.svg)

# `wm` - Website Monitor

> A simple monitoring tool 🔭 to track response times and HTTP status for URLs using Kafka 🐞 and Postgres 🐘.

`wm` has three sub-commands:

* `probe`: 📞 Requests a URL and publishes its HTTP status code, response time and a timestamp to a Kafka topic.
* `flush`: 📒 Consumes results from a Kafka topic and writes them to a Postgres instance.
* `stats`: 📊 Displays performance statistics for each URL with percentiles.

```shell
pip install wm

wm --help
```

Tested with Python 3.9 and services hosted by [Aiven](https://aiven.io).

See open issues for outstanding todos.

See [discussion](#Discussion) for notes on design decisions, areas of improvement and known issues.

## Example

```shell
for i in {1..10}; do
  wm probe \
    --url="https://example.com" \
    --bootstrap-server="my-kafka:1234" \
    --topic="my-website-monitor" \
    --ssl \
    --ssl-cafile="my-kafka.pem" \
    --ssl-certfile="my-kafka.cert" \
    --ssl-keyfile="my-kafka.key"

  sleep 1;
done

wm flush \
  --db-connection-string="postgres:my-postgres:5432" \
  --bootstrap-server="my-kafka:1234" \
  --topic="my-website-monitor" \
  --consumer-group-id="$WM_STREAM_CONSUMER_GROUP_ID" \
  --ssl \
  --ssl-cafile="my-kafka.pem" \
  --ssl-certfile="my-kafka.cert" \
  --ssl-keyfile="my-kafka.key"

wm stats \
  --db-connection-string="postgres:my-postgres:5432"
```
Will produce stats like this:
```json
{
  "stats": [
    {
      "url": "https://example.com",
      "probes": 10,
      "p50_ms": 592.0,
      "p95_ms": 832.0,
      "p99_ms": 868.0
    }
  ]
}

```

## Example deployment ☸️

See `example-deployment/` for an example deployment to Kubernetes. It runs periodic probes of a URL in one pod and
flushes the results from another.

## Discussion

Let's talk about design decisions, areas of improvement and known issues. See issues for outstanding todos.

The `website_monitor` leaves it to the user to implement periodic probing of a URL. This can be viewed as a merit but
also as a drawback. For one, it lends itself well as a CLI and can be easily run periodically by wrapping it with a
Bash `for` or `while` loop. On the other hand it puts the burden on the deployment to run it periodically if that is
desired. However, platforms like Kubernetes have cron jobs. Alternatively, one could have implemented long-running
processes.

The use of Kafka is naïve and possibly wasteful. This is to be blamed on my ignorance of Kafka and its patterns.

Every component blocks until it's done. While this makes for easy testing and CLI usage it might not make for the most
efficient and performant design. Every invocation opens and closes a connection to Postgres or Kafka. This is possibly
wasteful.

The statistics list p50, p95 and p99 percentiles for response times per URL but do not factor in HTTP status code or
temporal distribution.

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

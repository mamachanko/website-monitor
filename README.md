# Website Monitor

> A simple monitoring tool to track status and response times for URLs.

## Configuration
envs namespace with `WM` (short for _website monitor_)
```
WM_URL
WM_DB_CONNECTION_STRING
WM_STREAM_BOOTSTRAP_SERVERS
WM_STREAM_TOPIC
WM_STREAM_CONSUMER_GROUP_ID
WM_STREAM_SSL_CA_FILE
WM_STREAM_SSL_CERT_FILE
WM_STREAM_SSL_KEY_FILE
```

## Running
depends on Python 3.9

```shell
python -m website_monitor.probe_and_publish
python -m website_monitor.consume_and_write
python -m website_monitor.show_stats
```

### Examples

[comment]: <> (TODO)
```shell
$ WM_URL python -m website_monitor.probe_and_publish
$ python -m website_monitor.consume_and_write
$ python -m website_monitor.show_stats | yq r -
results:
  - url: https://httpbin.org
    probes_total: 3
    percentiles:
      p50_ms: 2000.0
      p50_ms: 2900.0
      p95_ms: 2980.0
  - url: https://httpbin.org/status/201
    probes_total: 1
    percentiles:
      p50_ms: 544.0
      p50_ms: 544.0
      p95_ms: 544.0
```

## Design decisions

 * does not run periodically by itself
 * Kafka connectors

## Example deployment
See example-deployment

## Know issues and short-comings
 * NoBrokersAvailable
 * heavy integration testing
 * db performance
 * repository duplicated code
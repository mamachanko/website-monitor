#!/usr/bin/env bash

set -euo pipefail

main() {
  create_stream
  create_database
  wait_until_running
  create_topics
}

create_stream() {
  avn service create stream \
    --service-type kafka \
    --plan startup-2 \
    --cloud google-europe-west3
}

create_database() {
  avn service create database \
    --service-type pg \
    --plan hobbyist \
    --cloud google-europe-west3
}

wait_until_running() {
  while true; do
    pending_services="$(
      avn service list --format '{service_name}' \
        | xargs -n1 avn service get --format '{state}' \
        | grep --count --invert-match RUNNING
    )"

    if [ "$pending_service" -eq 0 ]; then
      break
    else
      sleep 2
    fi
  done
}

create_topics() {
  avn service topic-create stream \
    website_monitor \
    --partitions 1 \
    --replication 2

  avn service topic-create stream \
    website_monitor_test \
    --partitions 1 \
    --replication 2
}

main
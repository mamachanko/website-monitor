#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

./clean.sh

kubectl create secret generic website-monitor-config \
  --from-literal=wm.url="${WM_URL:?}"\
  --from-literal=wm.db.connection-string="${WM_DB_CONNECTION_STRING:?}" \
  --from-literal=wm.stream.bootstrap-servers="${WM_STREAM_BOOTSTRAP_SERVERS:?}" \
  --from-literal=wm.stream.topic="${WM_STREAM_TOPIC:?}" \
  --from-literal=wm.stream.consumer_group_id="${WM_STREAM_CONSUMER_GROUP_ID:?}" \
  --from-literal=wm.stream.ssl_ca_file="${WM_STREAM_SSL_CA_FILE:?}" \
  --from-literal=wm.stream.ssl_cert_file="${WM_STREAM_SSL_CERT_FILE:?}" \
  --from-literal=wm.stream.ssl_key_file="${WM_STREAM_SSL_KEY_FILE:?}"

kubectl apply \
  --filename probe_and_publish_pod.yml \
  --filename consume_and_write_pod.yml

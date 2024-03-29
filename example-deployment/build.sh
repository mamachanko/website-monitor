#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

image_name="mamachanko/wm:latest"

docker build \
  .. \
  --file Dockerfile \
  --tag "$image_name"

docker push "$image_name"

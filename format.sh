#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

black \
  website_monitor/ \
  tests/

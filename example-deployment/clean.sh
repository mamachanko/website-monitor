#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

kubectl delete secret --all
kubectl delete pod --all --grace-period=0 --force

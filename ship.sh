#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

main() {
  echo "🚢 let's ship ..."

  assert_git_clean
  assert_formatted
  assert_pushable

  run_tests

  push
}

assert_git_clean() {
  assert_git_index_clean
  assert_git_work_dir_clean
}

assert_git_index_clean() {
  if ! git diff --exit-code --cached >/dev/null; then
    log_error "there are uncommitted changes in the index"
    exit 1
  else
    log_success "git index clean"
  fi
}

assert_git_work_dir_clean() {
  if ! git diff --exit-code >/dev/null ||
    git status --porcelain | grep '??'; then
    log_error "there are uncommitted changes in the working directory"
    exit 1
  else
    log_success "git work dir clean"
  fi
}

assert_formatted() {
  if ! black --check website_monitor/ tests/ 2>/dev/null; then
    log_error "code is not formatted"
    exit 1
  else
    log_success "code is formatted"
  fi
}

assert_pushable() {
  # Inspired by: https://stackoverflow.com/a/3278427

  git fetch origin

  local local=$(git rev-parse @)
  local remote=$(git rev-parse @{upstream})
  local base=$(git merge-base @ @{upstream})

  if [[ "$local" = "$remote" || "$remote" = "$base" ]]; then
    echo "✅ $(tput setab 28)good to push$(tput sgr0)"
  elif [ "$local" = "$base" ]; then
    log_error "upstream is ahead. please, rebase."
    exit 1
  else
    log_error "you have diverged from upstream. please, rebase."
    exit 1
  fi
}

log_error() {
  local error_message=${1:?}

  echo "❌ $(tput setab 124)$error_message$(tput sgr0)"
}

log_success() {
  local success_message=${1:?}

  echo "✅ $(tput setab 28)$success_message$(tput sgr0)"
}

run_tests() {
  pytest -vv
  log_success "tests pass"
}

push() {
  git push
  echo "🚢 successfully shipped"
}

main

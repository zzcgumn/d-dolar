#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/third_party/dds"

if ! command -v bazelisk >/dev/null 2>&1; then
  echo "error: bazelisk not found on PATH (see docs/dds3_build.md)" >&2
  exit 1
fi

bazelisk build -c opt //python:dds3_wheel_dist

wheel=$(find bazel-bin/python -name 'dds3-*.whl' | head -1)
if [ -z "$wheel" ]; then
  echo "error: build succeeded but no dds3-*.whl was found under bazel-bin/python" >&2
  exit 1
fi

pip install --force-reinstall "$wheel"
echo "Installed: $wheel"

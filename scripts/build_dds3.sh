#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT/third_party/dds"

if ! command -v bazelisk >/dev/null 2>&1; then
  echo "error: bazelisk not found on PATH (see docs/dds3_build.md)" >&2
  exit 1
fi

# DDS's own MODULE.bazel registers only a Python 3.14 toolchain by
# default, which produces an extension incompatible with any older
# CPython (confirmed: importing it under 3.12 fails with
# "symbol not found ... _PyDict_GetItemStringRef", a 3.13+ CPython C-API
# addition). Target whatever interpreter `pip` actually resolves to.
py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
bazelisk build -c opt \
  "--@rules_python//python/config_settings:python_version=${py_version}" \
  //python:dds3_wheel_dist

wheel=$(find bazel-bin/python -name 'dds3-*.whl' | head -1)
if [ -z "$wheel" ]; then
  echo "error: build succeeded but no dds3-*.whl was found under bazel-bin/python" >&2
  exit 1
fi

pip install --force-reinstall "$wheel"
echo "Installed: $wheel"

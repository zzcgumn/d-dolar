# Building dds3

`third_party/dds` is a git submodule (see
[`specs/dds3-dependency.md`](../specs/dds3-dependency.md) for what it is
and why). It is not built automatically — do this once, or whenever the
submodule's pinned commit changes.

## Prerequisites

- [`bazelisk`](https://github.com/bazelbuild/bazelisk) on `PATH`
  (`brew install bazelisk` on macOS).
- Python. Verified working with **3.12.11 on Darwin arm64** (macOS,
  Apple Silicon) — `scripts/build_dds3.sh` targets whichever Python
  version the active `python3`/`pip` actually is, so other 3.x versions
  should work too, but only 3.12 has actually been confirmed.
- A C++ compiler (clang 15+ or GCC 11+). On macOS, Bazel downloads its
  own pinned LLVM toolchain automatically — no separate install needed.

## Build

```bash
git submodule update --init third_party/dds
./scripts/build_dds3.sh
```

Confirm it worked:
```bash
python -c "import dds3; print(dds3.__file__)"
```

`dds-bridge/dds`'s own `MODULE.bazel` registers only a Python 3.14
toolchain by default. Building without an explicit version override
produces an extension that fails to import under any older CPython
(`ImportError: ... symbol not found ... _PyDict_GetItemStringRef`, a
3.13+ CPython C-API addition) — `scripts/build_dds3.sh` already passes
`--@rules_python//python/config_settings:python_version` set to whatever
`python3` actually reports, so this should not need manual handling.

## Troubleshooting

See `third_party/dds/docs/python_interface.md`'s own "Troubleshooting"
section — this project does not duplicate it. The most common issue is a
slow first-time toolchain/dependency download that looks stuck but isn't.

## Windows

Not supported — DDS's own Python build does not officially support it.

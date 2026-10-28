# dds3 (vendored DDS 3.1.1)

The contract for `third_party/dds`: a pinned, buildable copy of
`dds-bridge/dds`'s own first-party Python module, `dds3`, vendored as a
git submodule rather than a pip dependency (it has no PyPI release; its
own build system is Bazel).

## Behaviour & invariants

### What's vendored, and why a submodule

`third_party/dds` is `dds-bridge/dds` pinned at commit
`cd953c24a68cb8117bff4fcfd1807ad18a197f6c` (tag `v3.1.1`, an annotated tag
that dereferences to this commit). Apache-2.0 licensed, matching
d-dolar's own license. A submodule commits only a pointer to that
commit, not the vendored source itself.

### Building it

`scripts/build_dds3.sh` builds `//python:dds3_wheel_dist` with
`bazelisk` and `pip install`s the resulting wheel into whichever
venv/interpreter `pip` currently resolves to. This is deliberately not
part of `pip install -e ".[dev]"` — see `docs/dds3_build.md` for the full
build/install walkthrough.

**A real build-time finding**: `dds-bridge/dds`'s own `MODULE.bazel`
registers only a Python 3.14 toolchain by default. Building with no
override produces an extension that fails to import under any older
CPython (`ImportError: ... symbol not found ... _PyDict_GetItemStringRef`,
a 3.13+ CPython C-API addition) — confirmed directly against a Python
3.12 venv. `scripts/build_dds3.sh` passes
`--@rules_python//python/config_settings:python_version`, set to whatever
the active `python3` actually reports, to build an ABI-compatible
extension instead.

### What's guaranteed, and what isn't

`tests/test_dds3_smoke.py` (skipped, not failed, when `dds3` hasn't been
built) confirms: `dds3` is importable, `analyse_play_pbn` and
`calc_all_tables_pbn` return the documented shape, and both agree
exactly with a RawDB fixture hand's already-known `DD_W_C`/`DD_W_N`
values (12 each) — computed independently, by a different DDS build
(`endplay`/DDS 2.9.0, via `bridge-deals-ingest`). Two specific shape
details turned out to differ from what reading `docs/python_interface.md`
in isolation suggested, confirmed only once the build could actually be
run:

- `analyse_play_pbn`'s `"number"` is `len(result["tricks"])`, not a count
  of cards played (the two coincide only for a 1-card play).
- `calc_all_tables_pbn`'s `"no_of_boards"` reports `20` for a single
  submitted deal — DDS's traditional 20-board batch-chunk capacity
  leaking through the wrapper, not an actual board count.
  `len(result["tables"])` is the real count, and is correct.

DDS's own solver correctness is **not** re-validated here beyond that one
cross-check — that is upstream's own test suite's job (`python/tests/` at
the pinned commit), not d-dolar's to repeat.

## Out of scope

- Implementing D-dolar or either of the other two statistics with
  `dds3` — this package only gets the dependency built and callable.
- A d_dolar-side convenience wrapper around `dds3`'s PBN/bitmask API.
- Windows support (`dds3`'s own Python build is not officially supported
  there, per its `docs/python_interface.md`).

---
last-updated: 2026-10-28
related-plans: add-dds3-dependency
